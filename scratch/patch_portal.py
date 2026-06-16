import re

with open('portal_template.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace '/api/db-sync-table' with '/api/portal-upsert-records'
content = content.replace("'/api/db-sync-table'", "'/api/portal-upsert-records'")
content = content.replace('"/api/db-sync-table"', '"/api/portal-upsert-records"')

# 2. Add openModal right next to closeModal
close_modal_def = """        function closeModal(id) {
            document.getElementById(id).style.display = 'none';
        }"""
open_modal_def = """        function openModal(id) {
            document.getElementById(id).style.display = 'flex';
        }

        function closeModal(id) {
            document.getElementById(id).style.display = 'none';
        }"""
content = content.replace(close_modal_def, open_modal_def)

# 3. Fix const overallStatus crash in renderGestioneAccettazioni
const_status = "const overallStatus = 'collected';"
let_status = "let overallStatus = 'collected';"
content = content.replace(const_status, let_status)

# 4. Fix unsafe date parsing crash in renderGestioneAccettazioni
unsafe_date = "const sessionDate = new Date(g.collected_at).toISOString().split('T')[0];"
safe_date = "const sessionDate = g.collected_at ? g.collected_at.split(' ')[0].split('T')[0] : '';"
content = content.replace(unsafe_date, safe_date)

# 5. Add print prompt modal HTML
print_prompt_html = """    <!-- MODAL: STAMPA ACCETTAZIONE -->
    <div class="modal-overlay" id="modal-lis-print-prompt" style="display: none;">
        <div class="modal-box" style="max-width: 480px;">
            <div class="modal-header">
                <h2>Accettazione LIS - Stampa Documenti</h2>
                <button type="button" class="modal-close" onclick="closeModal('modal-lis-print-prompt')">&times;</button>
            </div>
            <div class="modal-body" style="padding: 20px; text-align: center;">
                <i data-lucide="printer" style="width: 48px; height: 48px; color: var(--primary); margin-bottom: 15px; display: inline-block;"></i>
                <h3 style="margin-bottom:8px;">Accettazione LIS Registrata con Successo!</h3>
                <p class="text-muted" style="font-size: 0.85rem; margin-bottom: 20px;">
                    Campione Barcode: <strong id="print-prompt-barcode-label" style="font-family:monospace; font-size:1.1rem; color:var(--text-primary);">000000000000</strong>
                </p>
                <input type="hidden" id="print-prompt-sample-id">
                <input type="hidden" id="print-prompt-invoice-id">
                <div style="display:flex; flex-direction:column; gap:12px; max-width: 320px; margin: 0 auto;">
                    <button type="button" class="btn btn-primary" onclick="printLisAcceptanceReceiptFromPrompt()"><i data-lucide="file-text" style="width:14px;height:14px;vertical-align:middle;margin-right:6px;"></i> Stampa Distinta Accettazione</button>
                    <button type="button" class="btn btn-success" onclick="printLisBarcodeLabelFromPrompt()"><i data-lucide="barcode" style="width:14px;height:14px;vertical-align:middle;margin-right:6px;"></i> Stampa Etichetta Barcode</button>
                    <button type="button" class="btn" style="background: #f97316; border-color: #f97316; color: white;" onclick="printLisConsentFromPrompt()"><i data-lucide="file-signature" style="width:14px;height:14px;vertical-align:middle;margin-right:6px;"></i> Stampa Consenso Informato</button>
                    <button type="button" class="btn btn-info" onclick="printInvoicePortalFromPrompt()"><i data-lucide="printer" style="width:14px;height:14px;vertical-align:middle;margin-right:6px;"></i> Stampa Fattura / Ricevuta</button>
                </div>
            </div>
            <div class="modal-footer" style="justify-content:center;">
                <button type="button" class="btn btn-secondary" onclick="closeModal('modal-lis-print-prompt')">Chiudi e Prosegui</button>
            </div>
        </div>
    </div>

    <!-- MODAL: REGISTRA PAZIENTE INLINE -->"""
content = content.replace("<!-- MODAL: REGISTRA PAZIENTE INLINE -->", print_prompt_html)

# 6. Add print prompt helper functions before closing script tag
print_helpers = """        function printLisBarcodeLabelFromPrompt() {
            const sampleId = parseInt(document.getElementById('print-prompt-sample-id').value);
            if (sampleId) printLisBarcodeLabel(sampleId);
        }

        function printLisAcceptanceReceiptFromPrompt() {
            const sampleId = parseInt(document.getElementById('print-prompt-sample-id').value);
            if (sampleId) printLisAcceptanceReceipt(sampleId);
        }

        function printLisConsentFromPrompt() {
            const sampleId = parseInt(document.getElementById('print-prompt-sample-id').value);
            if (!sampleId) return;
            const sample = allSamples.find(s => s.id === sampleId);
            if (!sample) return;
            const patient = allPatients.find(p => p.id === sample.patient_id);
            if (!patient) return;
            
            const sampleTests = allTests.filter(t => t.sample_id === sampleId);
            const serviceIds = sampleTests.map(t => t.service_id);
            
            stampaPrivacyGdpr(patient);
            stampaConsensiLisObbligatori(patient, serviceIds);
        }

        function printInvoicePortalFromPrompt() {
            const invoiceId = parseInt(document.getElementById('print-prompt-invoice-id').value);
            if (invoiceId) printInvoicePortal(invoiceId);
        }
"""

# We find the last occurrences of closing script tag and insert helpers before it
last_script_idx = content.rfind('</script>')
if last_script_idx != -1:
    content = content[:last_script_idx] + print_helpers + content[last_script_idx:]

# 7. Modify print logic in salvaAccettazione()
old_print_block = """                        apiCall('/api/portal-upsert-records', { table_name: 'invoices', rows: existingInvoices }, (iRes) => {
                            apiCall('/api/portal-upsert-records', { table_name: 'lis_collection_points', rows: allCollectionPoints }, (cpRes) => {
                                alert("Accettazione completata con successo!\\nFattura emessa: " + invoiceNum + "\\n\\n" + barcodePromptText);
                                
                                // Stampiamo consensi privacy GDPR e LIS
                                const patient = allPatients.find(p => p.id === patientId);
                                const serviceIds = selectedServices.map(s => s.id);
                                if (patient) {
                                    stampaPrivacyGdpr(patient);
                                    stampaConsensiLisObbligatori(patient, serviceIds);
                                }

                                // Stampiamo etichette provette, ricevuta accettazione e fattura
                                const firstSampleId = newSamplesList[0].id;
                                if (typeof printLisBarcodeLabel === 'function') printLisBarcodeLabel(firstSampleId);
                                if (typeof printLisAcceptanceReceipt === 'function') printLisAcceptanceReceipt(firstSampleId);
                                if (typeof printInvoicePortal === 'function') printInvoicePortal(invoiceId);

                                document.getElementById('sam-patient-search').value = '';
                                document.getElementById('sam-patient').value = '';
                                document.getElementById('btn-edit-patient').style.display = 'none';
                                selectedServices = [];
                                renderSelectedTags();
                                
                                loadData();
                            });
                        });"""

new_print_block = """                        apiCall('/api/portal-upsert-records', { table_name: 'invoices', rows: existingInvoices }, (iRes) => {
                            apiCall('/api/portal-upsert-records', { table_name: 'lis_collection_points', rows: allCollectionPoints }, (cpRes) => {
                                // Set prompt values and show modal
                                const firstSampleId = newSamplesList[0].id;
                                const firstBarcode = newSamplesList[0].barcode;
                                document.getElementById('print-prompt-sample-id').value = firstSampleId;
                                document.getElementById('print-prompt-barcode-label').innerText = firstBarcode;
                                document.getElementById('print-prompt-invoice-id').value = invoiceId;
                                
                                openModal('modal-lis-print-prompt');

                                // Reset UI
                                document.getElementById('sam-patient-search').value = '';
                                document.getElementById('sam-patient').value = '';
                                document.getElementById('btn-edit-patient').style.display = 'none';
                                selectedServices = [];
                                renderSelectedTags();
                                
                                loadData();
                            });
                        });"""

content = content.replace(old_print_block, new_print_block)

with open('portal_template.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("portal_template.html patched successfully!")
