import java.io.File;
import java.nio.file.Files;
import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.Date;
import org.mustangproject.CalculatedInvoice;
import org.mustangproject.Invoice;
import org.mustangproject.Product;
import org.mustangproject.ZUGFeRD.IZUGFeRDExportableItem;
import org.mustangproject.ZUGFeRD.ZUGFeRDInvoiceImporter;

/** A deliberately narrow view of fields exposed by the pinned Mustang importer. */
public final class SourceCheckBridge {
    static String q(Object value) {
        if (value == null) return "null";
        String s = value instanceof Date
            ? DateTimeFormatter.ISO_LOCAL_DATE.withZone(ZoneId.systemDefault()).format(((Date) value).toInstant())
            : value.toString();
        StringBuilder b = new StringBuilder("\"");
        for (char c : s.toCharArray()) {
            switch (c) {
                case '\\': b.append("\\\\"); break;
                case '"': b.append("\\\""); break;
                case '\n': b.append("\\n"); break;
                case '\r': b.append("\\r"); break;
                case '\t': b.append("\\t"); break;
                default: if (c < 32) b.append(String.format("\\u%04x", (int)c)); else b.append(c);
            }
        }
        return b.append('"').toString();
    }
    static void field(StringBuilder b, String name, Object value) {
        if (b.length() > 1 && b.charAt(b.length() - 1) != '{') b.append(',');
        b.append(q(name)).append(':').append(q(value));
    }
    public static void main(String[] args) throws Exception {
        if (args.length != 1) throw new IllegalArgumentException("Expected one XML path");
        byte[] xml = Files.readAllBytes(new File(args[0]).toPath());
        ZUGFeRDInvoiceImporter importer = new ZUGFeRDInvoiceImporter();
        importer.setRawXML(xml);
        Invoice invoice = importer.extractInvoice();
        StringBuilder b = new StringBuilder("{");
        field(b, "number", invoice.getNumber());
        field(b, "issue_date", invoice.getIssueDate());
        field(b, "due_date", invoice.getDueDate());
        field(b, "currency", invoice.getCurrency());
        field(b, "buyer_order", invoice.getBuyerOrderReferencedDocumentID());
        field(b, "seller_order", invoice.getSellerOrderReferencedDocumentID());
        field(b, "payment_reference", invoice.getPaymentReference());
        field(b, "payment_terms", invoice.getPaymentTermDescription());
        field(b, "delivery_note", invoice.getDeliveryNoteReferencedDocumentID());
        Object contract = invoice.getClass().getMethod("getContractReferencedDocument").invoke(invoice);
        if (contract != null && !(contract instanceof String)) {
            contract = contract.getClass().getMethod("getIssuerAssignedID").invoke(contract);
        }
        field(b, "contract_reference", contract);
        if (invoice instanceof CalculatedInvoice) {
            CalculatedInvoice calculated = (CalculatedInvoice) invoice;
            field(b, "grand_total", calculated.getGrandTotal());
            field(b, "due_payable", calculated.getDuePayable());
        }
        b.append(",\"lines\":[");
        IZUGFeRDExportableItem[] lines = invoice.getZFItems();
        if (lines != null) for (int i = 0; i < lines.length; i++) {
            if (i > 0) b.append(',');
            IZUGFeRDExportableItem line = lines[i];
            b.append('{');
            field(b, "id", line.getId());
            field(b, "quantity", line.getQuantity());
            field(b, "price", line.getPrice());
            Product product = (Product) line.getProduct();
            field(b, "name", product == null ? null : product.getName());
            field(b, "description", product == null ? null : product.getDescription());
            b.append('}');
        }
        b.append("]}");
        System.out.println(b);
    }
}
