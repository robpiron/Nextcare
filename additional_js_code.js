// ADDITIONAL NEXTCARE MODULES: COMPANIES, RIS TEMPLATES, LIS BULK ACC & BI DASHBOARD

// -------------------------------------------------------------
// MODULE 1: COMPANIES & CUMULATIVE BILLING
// -------------------------------------------------------------

window.switchHrisSubTab = function(tabName) {
    const btnStaff = document.getElementById('sub-tab-hris-staff');
    const btnCompanies = document.getElementById('sub-tab-hris-companies');
    const paneStaff = document.getElementById('hris-staff-pane');
    const paneCompanies = document.getElementById('hris-companies-pane');

    if (btnStaff) btnStaff.classList.remove('active');
    if (btnCompanies) btnCompanies.classList.remove('active');

    if (paneStaff) paneStaff.style.display = 'none';
    if (paneCompanies) paneCompanies.style.display = 'none';

    if (tabName === 'companies') {
        if (btnCompanies) btnCompanies.classList.add('active');
        if (paneCompanies) paneCompanies.style.display = 'block';
        window.renderCompanies();
    } else {
        if (btnStaff) btnStaff.classList.add('active');
        if (paneStaff) paneStaff.style.display = 'block';
        if (typeof renderStaffAndShifts === 'function') renderStaffAndShifts();
    }
    if (window.lucide) window.lucide.createIcons();
};

window.populateCompaniesDropdown = function(selectId) {
    const el = document.getElementById(selectId);
    if (!el) return;
    const companies = DB.get('companies') || [];
    el.innerHTML = '<option value="">-- Nessuna Azienda Convenzionata --</option>';
    companies.forEach(c => {
        el.innerHTML += `<option value="${c.id}">${c.name}</option>';
    });
};

window.renderCompanies = function() {
    const tbody = document.querySelector('#companies-table tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    
    const companies = DB.get('companies') || [];
    const pricelists = DB.get('price_lists') || [];

    if (companies.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;" class="text-muted">Nessuna azienda registrata</td></tr>';
        return;
    }

    companies.forEach(c => {
        const pl = pricelists.find(p => p.id == c.price_list_id);
        const plName = pl ? pl.name : `Listino ${c.price_list_id}`;
        const bType = c.billing_type === 'company_post' ? 'Cumulativo Post-Hoc' : 'Fattura al Paziente';
        
        tbody.innerHTML += `
            <tr>
                <td><strong>${c.name}</strong></td>
                <td>P.IVA: ${c.vat_number}<br><small class="text-muted">C.F: ${c.fiscal_code || '-'}</small></td>
                <td>${c.address || '-'}<br><small class="text-muted">${c.email || ''}</small></td>
                <td><span class="badge ${c.billing_type === 'company_post' ? 'badge-warning' : 'badge-info'}">${bType}</span></td>
                <td>${plName}</td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="window.openAddCompanyModal(${c.id})"><i data-lucide="edit" style="width:12px;height:12px;"></i></button>
                    <button class="btn btn-danger btn-sm" onclick="window.deleteCompany(${c.id})"><i data-lucide="trash-2" style="width:12px;height:12px;"></i></button>
                </td>
            </tr>
        `;
    });
    if (window.lucide) window.lucide.createIcons();
};

window.openAddCompanyModal = function(coId = null) {
    document.getElementById('form-add-company').reset();
    window.populatePriceListsDropdown('company-pricelist');

    if (coId) {
        const companies = DB.get('companies') || [];
        const c = companies.find(item => item.id === coId);
        if (c) {
            document.getElementById('company-modal-title').innerText = "Modifica Azienda Convenzionata";
            document.getElementById('company-id').value = c.id;
            document.getElementById('company-name').value = c.name;
            document.getElementById('company-vat').value = c.vat_number;
            document.getElementById('company-address').value = c.address || '';
            document.getElementById('company-email').value = c.email || '';
            document.getElementById('company-phone').value = c.phone || '';
            document.getElementById('company-pricelist').value = c.price_list_id;
            document.getElementById('company-billing-type').value = c.billing_type;
        }
    } else {
        document.getElementById('company-modal-title').innerText = "Nuova Azienda Convenzionata";
        document.getElementById('company-id').value = '';
        document.getElementById('company-pricelist').value = 1;
    }
    openModal('modal-add-company');
};

window.handleCompanySubmit = async function(e) {
    e.preventDefault();
    const idVal = document.getElementById('company-id').value;
    const name = document.getElementById('company-name').value;
    const vat = document.getElementById('company-vat').value;
    const address = document.getElementById('company-address').value;
    const email = document.getElementById('company-email').value;
    const phone = document.getElementById('company-phone').value;
    const pricelistId = parseInt(document.getElementById('company-pricelist').value);
    const billingType = document.getElementById('company-billing-type').value;

    const company = {
        name,
        vat_number: vat,
        fiscal_code: vat,
        address,
        email,
        phone,
        price_list_id: pricelistId,
        billing_type: billingType
    };

    if (idVal) {
        const coId = parseInt(idVal);
        company.id = coId;
        DB.update('companies', coId, company);
        DB.logAudit(4, "COMPANY_UPDATE", "companies", coId, { name });
    } else {
        const newCo = DB.insert('companies', company);
        DB.logAudit(4, "COMPANY_CREATE", "companies", newCo.id, { name });
    }

    await DB.waitForSync();
    closeModal('modal-add-company');
    window.renderCompanies();
    alert("Azienda salvata e sincronizzata con successo!");
};

window.deleteCompany = async function(coId) {
    if (!confirm("Sei sicuro di voler eliminare questa azienda convenzionata?")) return;
    DB.delete('companies', coId);
    DB.logAudit(4, "COMPANY_DELETE", "companies", coId, {});
    await DB.waitForSync();
    window.renderCompanies();
    alert("Azienda eliminata.");
};

window.openCumulativeBillingModal = function() {
    const select = document.getElementById('billing-company-select');
    if (!select) return;
    select.innerHTML = '<option value="">-- Seleziona Azienda --</option>';
    const companies = DB.get('companies') || [];
    const postCompanies = companies.filter(c => c.billing_type === 'company_post');
    postCompanies.forEach(c => {
        select.innerHTML += `<option value="${c.id}">${c.name}</option>';
    });

    document.getElementById('billing-date-from').value = '';
    document.getElementById('billing-date-to').value = '';
    document.getElementById('billing-items-table').querySelector('tbody').innerHTML = '<tr><td colspan="5" style="text-align:center;" class="text-muted">Seleziona azienda convenzionata e periodo di fatturazione</td></tr>';
    document.getElementById('billing-subtotal').innerText = '€ 0,00';
    document.getElementById('billing-vat').innerText = '€ 0,00';
    document.getElementById('billing-total').innerText = '€ 0,00';
    document.getElementById('billing-count-badge').innerText = '0 prestazioni';
    document.getElementById('btn-emit-cumulative').disabled = true;

    openModal('modal-cumulative-billing');
};

window.calculateCumulativeInvoices = function() {
    const coId = document.getElementById('billing-company-select').value;
    const dateFrom = document.getElementById('billing-date-from').value;
    const dateTo = document.getElementById('billing-date-to').value;
    const tbody = document.getElementById('billing-items-table').querySelector('tbody');
    
    if (!coId) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;" class="text-muted">Seleziona un\'azienda convenzionata</td></tr>';
        return;
    }

    const invoices = DB.get('invoices') || [];
    const patients = DB.get('patients') || [];
    const appointments = DB.get('appointments') || [];
    const appServices = DB.get('appointment_services') || [];
    const services = DB.get('medical_services') || [];
    const pricelists = DB.get('price_lists') || [];

    // Filter invoices linked to this company, unpaid, is_company_post = 1
    let filteredInvoices = invoices.filter(inv => {
        if (inv.company_id != coId) return false;
        if (inv.is_company_post != 1) return false;
        if (inv.payment_status === 'paid') return false;
        if (dateFrom && inv.issue_date < dateFrom) return false;
        if (dateTo && inv.issue_date > dateTo) return false;
        return true;
    });

    tbody.innerHTML = '';
    if (filteredInvoices.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;" class="text-muted">Nessuna prestazione non fatturata trovata per questo periodo.</td></tr>';
        document.getElementById('billing-subtotal').innerText = '€ 0,00';
        document.getElementById('billing-vat').innerText = '€ 0,00';
        document.getElementById('billing-total').innerText = '€ 0,00';
        document.getElementById('billing-count-badge').innerText = '0 prestazioni';
        document.getElementById('btn-emit-cumulative').disabled = true;
        return;
    }

    let subtotalSum = 0;
    filteredInvoices.forEach(inv => {
        let patName = 'Paziente Esterno';
        let srvNames = 'Prestazioni Cliniche';
        
        // Find patient name
        let patId = null;
        if (inv.appointment_id) {
            const app = appointments.find(a => a.id === inv.appointment_id);
            if (app) patId = app.patient_id;
        } else if (inv.sample_id) {
            const sam = DB.get('lab_samples').find(s => s.id === inv.sample_id);
            if (sam) patId = sam.patient_id;
        } else if (inv.study_id) {
            const st = DB.get('radiology_studies').find(s => s.id === inv.study_id);
            if (st) patId = st.patient_id;
        }

        if (patId) {
            const p = patients.find(pat => pat.id === patId);
            if (p) patName = `${p.last_name.toUpperCase()} ${p.first_name}`;
        }

        // Find service names
        if (inv.appointment_id) {
            const sIds = appServices.filter(as => as.appointment_id === inv.appointment_id).map(as => as.service_id);
            srvNames = services.filter(s => sIds.includes(s.id)).map(s => s.name).join(', ') || 'Visite/Esami';
        } else if (inv.sample_id) {
            const tests = DB.get('lab_tests') || [];
            const sIds = tests.filter(t => t.sample_id === inv.sample_id).map(t => t.service_id);
            srvNames = services.filter(s => sIds.includes(s.id)).map(s => s.name).join(', ') || 'Analisi di Laboratorio';
        } else if (inv.study_id) {
            const st = DB.get('radiology_studies').find(s => s.id === inv.study_id);
            const srv = st ? services.find(s => s.id === st.service_id) : null;
            srvNames = srv ? srv.name : 'Esame RIS';
        }

        const pl = pricelists.find(p => p.id == inv.price_list_id);
        const plName = pl ? pl.name : 'Standard';

        tbody.innerHTML += `
            <tr>
                <td>${inv.issue_date}</td>
                <td><strong>${patName}</strong></td>
                <td>${srvNames}</td>
                <td>${plName}</td>
                <td><strong>€ ${inv.amount_due.toFixed(2)}</strong></td>
            </tr>
        `;
        subtotalSum += inv.amount_due;
    });

    const vatAmt = subtotalSum * 0.22; // Default 22% VAT for company services (e.g. medicine del lavoro)
    const totalAmt = subtotalSum + vatAmt;

    document.getElementById('billing-subtotal').innerText = `€ ${subtotalSum.toFixed(2)}`;
    document.getElementById('billing-vat').innerText = `€ ${vatAmt.toFixed(2)}`;
    document.getElementById('billing-total').innerText = `€ ${totalAmt.toFixed(2)}`;
    document.getElementById('billing-count-badge').innerText = `${filteredInvoices.length} prestazioni`;
    document.getElementById('btn-emit-cumulative').disabled = false;
};

window.emitCumulativeInvoice = async function() {
    const coId = document.getElementById('billing-company-select').value;
    const dateFrom = document.getElementById('billing-date-from').value;
    const dateTo = document.getElementById('billing-date-to').value;
    
    if (!coId) return;

    if (!confirm("Sei sicuro di voler emettere la fattura cumulativa ed azzerare i conti in sospeso per questa azienda?")) return;

    const invoices = DB.get('invoices') || [];
    const companies = DB.get('companies') || [];
    const company = companies.find(c => c.id == coId);
    if (!company) return;

    let subtotalSum = 0;
    const invoiceIdsUpdated = [];

    invoices.forEach(inv => {
        if (inv.company_id == coId && inv.is_company_post == 1 && inv.payment_status === 'unpaid') {
            if (dateFrom && inv.issue_date < dateFrom) return;
            if (dateTo && inv.issue_date > dateTo) return;
            
            inv.payment_status = 'paid';
            inv.payment_method = 'Bonifico Azienda';
            inv.paid_at = new Date().toISOString().split('T')[0];
            inv.amount_paid = inv.amount_due;
            
            invoiceIdsUpdated.push(inv.id);
            subtotalSum += inv.amount_due;
        }
    });

    const vatAmt = subtotalSum * 0.22;
    const totalAmt = subtotalSum + vatAmt;

    // Create cumulative document
    const invoiceNum = getNextInvoiceNumber();
    const cumulativeInvoice = {
        invoice_number: invoiceNum,
        issue_date: new Date().toISOString().split('T')[0],
        subtotal: subtotalSum,
        discount_value: 0,
        discount_type: 'flat',
        discount_amount: 0,
        price_list_id: company.price_list_id,
        claim_id: null,
        insurance_covered_amount: 0,
        stamp_duty: 2.00,
        amount_due: totalAmt + 2.00,
        amount_paid: 0.0,
        payment_status: 'unpaid',
        payment_method: null,
        paid_at: null,
        is_insurance_invoice: false,
        company_id: company.id,
        is_company_post: 0,
        custom_rates: { notes: `Fattura cumulativa per il periodo ${dateFrom || 'Inizio'} - ${dateTo || 'Fine'}. Contiene dettagli per ${invoiceIdsUpdated.length} esami.` }
    };

    DB.set('invoices', invoices); // update status of single entries
    DB.insert('invoices', cumulativeInvoice); // create cumulative document
    DB.logAudit(4, "CUMULATIVE_BILL_EMITTED", "invoices", null, { company_id: coId, invoice_number: invoiceNum, amount: totalAmt });

    await DB.waitForSync();
    closeModal('modal-cumulative-billing');
    if (typeof renderAdmissionsAndInvoices === 'function') renderAdmissionsAndInvoices();
    alert(`Fattura cumulativa emessa con successo! Generato documento ${invoiceNum} intestato a ${company.name} per un totale di € ${(totalAmt + 2.00).toFixed(2)}.`);
};

// -------------------------------------------------------------
// MODULE 2: AGENDAS CALENDAR REDESIGN (GOOGLE-STYLE)
// -------------------------------------------------------------

window.refreshCalendarData = async function() {
    const btn = document.querySelector('#modal-agendas-calendar button i[data-lucide="refresh-cw"]');
    if (btn) btn.classList.add('fa-spin');
    try {
        if (typeof window.syncFromMySQL === 'function') {
            await window.syncFromMySQL();
        }
        window.renderCalendarGrid();
    } catch (err) {
        console.error("Errore durante l'aggiornamento del calendario:", err);
    } finally {
        if (btn) btn.classList.remove('fa-spin');
    }
};

// -------------------------------------------------------------
// MODULE 3: RIS REPORTING MODELLI & TEMPLATE SELECTION
// -------------------------------------------------------------

window.handleRisRadiologistChange = function() {
    const radSelect = document.getElementById('dicom-radiologist');
    const tplSelect = document.getElementById('dicom-report-template');
    if (!radSelect || !tplSelect) return;

    const radId = radSelect.value;
    const studyIdVal = document.getElementById('dicom-study-id').value;
    if (!studyIdVal) return;

    const studyId = parseInt(studyIdVal);
    const study = (DB.get('radiology_studies') || []).find(s => s.id === studyId);
    if (!study) return;

    tplSelect.innerHTML = '<option value="">-- Seleziona Modello --</option>';

    const templates = DB.get('ris_report_templates') || [];
    const filtered = templates.filter(t => {
        // filter by service
        if (t.service_id && t.service_id !== study.service_id) return false;
        // filter by doctor
        if (radId) {
            let docIds = [];
            if (t.doctor_ids) {
                try {
                    docIds = Array.isArray(t.doctor_ids) ? t.doctor_ids : JSON.parse(t.doctor_ids);
                } catch(e){}
            }
            if (docIds.length > 0 && !docIds.map(String).includes(String(radId))) return false;
        }
        return true;
    });

    filtered.forEach(t => {
        tplSelect.innerHTML += `<option value="${t.id}">${t.title}</option>`;
    });
};

window.applySelectedRisTemplate = function() {
    const tplSelect = document.getElementById('dicom-report-template');
    const editor = document.getElementById('dicom-report-editor');
    if (!tplSelect || !editor) return;

    const tplId = tplSelect.value;
    if (!tplId) return;

    const templates = DB.get('ris_report_templates') || [];
    const t = templates.find(item => item.id == tplId);
    if (t) {
        // Prepend or overwrite
        if (confirm("Vuoi sovrascrivere il testo corrente con il modello selezionato?")) {
            editor.innerHTML = t.content;
        }
    }
};

window.toggleVoiceDictation = function() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("La dettatura vocale non è supportata da questo browser (usa Google Chrome o Microsoft Edge).");
        return;
    }

    const editor = document.getElementById('dicom-report-editor');
    const btn = document.getElementById('btn-ris-voice-dictation');
    const icon = document.getElementById('voice-mic-icon');

    if (window.risVoiceRecognitionRunning) {
        // Stop
        window.risVoiceRecognition.stop();
        window.risVoiceRecognitionRunning = false;
        btn.classList.remove('btn-success');
        btn.classList.add('btn-secondary');
        icon.style.color = '';
        btn.style.animation = '';
        return;
    }

    const rec = new SpeechRecognition();
    rec.lang = 'it-IT';
    rec.continuous = true;
    rec.interimResults = false;

    rec.onstart = function() {
        window.risVoiceRecognitionRunning = true;
        btn.classList.remove('btn-secondary');
        btn.classList.add('btn-success');
        icon.style.color = '#fff';
        btn.style.animation = 'pulse 1.5s infinite';
    };

    rec.onresult = function(event) {
        let finalTrans = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            if (event.results[i].isFinal) {
                finalTrans += event.results[i][0].transcript + ' ';
            }
        }
        if (finalTrans) {
            // Append to editor
            editor.innerHTML += finalTrans;
        }
    };

    rec.onerror = function(event) {
        console.error("Speech Recognition Error:", event.error);
        rec.stop();
    };

    rec.onend = function() {
        window.risVoiceRecognitionRunning = false;
        btn.classList.remove('btn-success');
        btn.classList.add('btn-secondary');
        icon.style.color = '';
        btn.style.animation = '';
    };

    window.risVoiceRecognition = rec;
    rec.start();
};

window.renderRisTemplatesTable = function() {
    const tbody = document.getElementById('ris-templates-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';

    const templates = DB.get('ris_report_templates') || [];
    const services = DB.get('medical_services') || [];
    const staff = DB.get('staff') || [];

    if (templates.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align:center;" class="text-muted">Nessun modello configurato.</td></tr>';
        return;
    }

    templates.forEach(t => {
        const srv = services.find(s => s.id == t.service_id);
        const sName = srv ? srv.name : 'Tutte le prestazioni RIS';

        let docList = 'Tutti i Medici';
        if (t.doctor_ids) {
            let docIds = [];
            try {
                docIds = Array.isArray(t.doctor_ids) ? t.doctor_ids : JSON.parse(t.doctor_ids);
            } catch(e){}
            if (docIds.length > 0) {
                docList = docIds.map(id => {
                    const st = staff.find(s => s.id == id);
                    return st ? `Dr. ${st.last_name}` : `Medico ${id}`;
                }).join(', ');
            }
        }

        tbody.innerHTML += `
            <tr>
                <td><strong>${t.title}</strong></td>
                <td>${sName}</td>
                <td><small>${docList}</small></td>
                <td>
                    <button class="btn btn-secondary btn-sm" onclick="window.openAddRisTemplateModal(${t.id})"><i data-lucide="edit" style="width:12px;height:12px;"></i></button>
                    <button class="btn btn-danger btn-sm" onclick="window.deleteRisTemplate(${t.id})"><i data-lucide="trash-2" style="width:12px;height:12px;"></i></button>
                </td>
            </tr>
        `;
    });
    if (window.lucide) window.lucide.createIcons();
};

window.openAddRisTemplateModal = function(tplId = null) {
    document.getElementById('form-add-ris-template').reset();
    
    // Populate RIS services dropdown
    const select = document.getElementById('ris-template-service');
    select.innerHTML = '<option value="">-- Associa a tutte le prestazioni RIS --</option>';
    const services = DB.get('medical_services') || [];
    const risSrv = services.filter(s => s.type === 'ris');
    risSrv.forEach(s => {
        select.innerHTML += `<option value="${s.id}">${s.name}</option>';
    });

    // Populate doctor checkboxes
    const container = document.getElementById('ris-template-doctors-checkboxes');
    container.innerHTML = '';
    const staff = DB.get('staff') || [];
    const doctors = staff.filter(s => s.role === 'doctor' && s.active === 1);
    doctors.forEach(doc => {
        container.innerHTML += `
            <label style="font-weight: 500; font-size: 0.8rem; display: flex; align-items: center; gap: 6px; cursor: pointer;">
                <input type="checkbox" class="ris-tpl-doctor-chk" value="${doc.id}">
                Dott. ${doc.last_name} ${doc.first_name}
            </label>
        `;
    });

    if (tplId) {
        const templates = DB.get('ris_report_templates') || [];
        const t = templates.find(item => item.id == tplId);
        if (t) {
            document.getElementById('ris-template-modal-title').innerText = "Modifica Modello Referto";
            document.getElementById('ris-template-id').value = t.id;
            document.getElementById('ris-template-title').value = t.title;
            document.getElementById('ris-template-service').value = t.service_id || '';
            document.getElementById('ris-template-content').value = t.content;

            let docIds = [];
            if (t.doctor_ids) {
                try {
                    docIds = Array.isArray(t.doctor_ids) ? t.doctor_ids : JSON.parse(t.doctor_ids);
                } catch(e){}
            }
            
            const chks = container.querySelectorAll('.ris-tpl-doctor-chk');
            chks.forEach(chk => {
                chk.checked = docIds.map(String).includes(String(chk.value));
            });
        }
    } else {
        document.getElementById('ris-template-modal-title').innerText = "Nuovo Modello Referto";
        document.getElementById('ris-template-id').value = '';
    }

    openModal('modal-add-ris-template');
};

window.handleRisTemplateSubmit = async function(e) {
    e.preventDefault();
    const idVal = document.getElementById('ris-template-id').value;
    const title = document.getElementById('ris-template-title').value;
    const serviceId = document.getElementById('ris-template-service').value ? parseInt(document.getElementById('ris-template-service').value) : null;
    const content = document.getElementById('ris-template-content').value;

    const chks = document.querySelectorAll('.ris-tpl-doctor-chk:checked');
    const doctorIds = Array.from(chks).map(c => parseInt(c.value));

    const tpl = {
        title,
        service_id: serviceId,
        content,
        doctor_ids: JSON.stringify(doctorIds)
    };

    if (idVal) {
        const tplId = parseInt(idVal);
        tpl.id = tplId;
        DB.update('ris_report_templates', tplId, tpl);
        DB.logAudit(4, "RIS_TEMPLATE_UPDATE", "ris_report_templates", tplId, { title });
    } else {
        const newTpl = DB.insert('ris_report_templates', tpl);
        DB.logAudit(4, "RIS_TEMPLATE_CREATE", "ris_report_templates", newTpl.id, { title });
    }

    await DB.waitForSync();
    closeModal('modal-add-ris-template');
    window.renderRisTemplatesTable();
    alert("Modello referto salvato e sincronizzato!");
};

window.deleteRisTemplate = async function(tplId) {
    if (!confirm("Rimuovere questo modello referto?")) return;
    DB.delete('ris_report_templates', tplId);
    DB.logAudit(4, "RIS_TEMPLATE_DELETE", "ris_report_templates", tplId, {});
    await DB.waitForSync();
    window.renderRisTemplatesTable();
    alert("Modello rimosso.");
};

// -------------------------------------------------------------
// MODULE 4: LIS MULTIPLE ACCEPTANCE & BULK SAMPLES CHECK-IN
// -------------------------------------------------------------

window.downloadMultipleAcceptanceTemplate = function() {
    const csvContent = "data:text/csv;charset=utf-8," 
        + "Cognome,Nome,Codice Fiscale,Genere,Data Nascita,Email,Telefono,Azienda ID\n"
        + "Rossi,Mario,RSSMRA80A01H501U,M,1980-01-01,mario.rossi@example.com,3331234567,1\n"
        + "Verdi,Laura,VRDLRA92M42F205K,F,1992-08-02,laura.verdi@example.com,3457654321,";
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "template_accettazione_multipla.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

window.handleMultipleAcceptanceUpload = function(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(e) {
        const text = e.target.result;
        const lines = text.split('\n');
        
        window.multipleAcceptancePatients = [];
        const tbody = document.querySelector('#multiple-acceptance-table tbody');
        tbody.innerHTML = '';

        const dbPatients = DB.get('patients') || [];
        const dbCompanies = DB.get('companies') || [];

        let count = 0;
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;
            const cols = line.split(',');
            if (cols.length < 5) continue;

            const lastName = cols[0].trim();
            const firstName = cols[1].trim();
            const taxCode = cols[2].trim().toUpperCase();
            const gender = cols[3].trim().toUpperCase();
            const birthDate = cols[4].trim();
            const email = cols[5] ? cols[5].trim() : '';
            const phone = cols[6] ? cols[6].trim() : '';
            const companyIdVal = cols[7] ? cols[7].trim() : '';
            
            const coId = companyIdVal ? parseInt(companyIdVal) : null;
            const company = dbCompanies.find(c => c.id === coId);
            const coName = company ? company.name : (coId ? `Azienda #${coId}` : 'Nessuna');

            const exists = dbPatients.some(p => p.tax_code === taxCode);
            const statusLabel = exists 
                ? '<span style="color:#10b981;font-weight:600;">Anagrafica Esistente</span>' 
                : '<span style="color:#2563eb;font-weight:600;">Nuova Anagrafica (Verrà creata)</span>';

            tbody.innerHTML += `
                <tr>
                    <td><strong>${lastName.toUpperCase()} ${firstName}</strong></td>
                    <td><code>${taxCode}</code></td>
                    <td>${gender} / ${birthDate}</td>
                    <td>${email}<br><small>${phone}</small></td>
                    <td>${coName}</td>
                    <td>${statusLabel}</td>
                </tr>
            `;

            window.multipleAcceptancePatients.push({
                last_name: lastName,
                first_name: firstName,
                tax_code: taxCode,
                gender,
                birth_date: birthDate,
                email,
                phone,
                company_id: coId,
                exists
            });
            count++;
        }

        document.getElementById('multiple-acceptance-preview-section').style.display = count > 0 ? 'block' : 'none';
        document.getElementById('multiple-acceptance-summary-text').innerText = `Caricati ${count} pazienti dall'importazione. Seleziona gli esami da associare a tutti.`;
        
        window.multipleAcceptanceSelectedTests = [];
        document.getElementById('bulk-selected-tests-tags').innerHTML = '';
        
        document.getElementById('btn-save-multiple-acceptance').disabled = count === 0;
    };
    reader.readAsText(file);
};

window.handleBulkSearchInput = function() {
    const input = document.getElementById('bulk-search-test');
    const dropdown = document.getElementById('bulk-search-results');
    if (!input || !dropdown) return;

    const val = input.value.toLowerCase().trim();
    if (!val) {
        dropdown.classList.add('hidden');
        return;
    }

    const services = DB.get('medical_services') || [];
    const lisSrv = services.filter(s => s.type === 'lis' && s.name.toLowerCase().includes(val));

    dropdown.innerHTML = '';
    if (lisSrv.length === 0) {
        dropdown.innerHTML = '<div style="padding:8px 12px;" class="text-muted">Nessun esame LIS trovato</div>';
    } else {
        lisSrv.forEach(s => {
            dropdown.innerHTML += `
                <div style="padding:8px 12px; cursor:pointer;" onclick="window.addBulkTestTag(${s.id}, '${s.name.replace(/'/g, "\\'")}')">
                    <strong>${s.name}</strong> <small class="text-muted">(${s.code || 'LIS'})</small>
                </div>
            `;
        });
    }
    dropdown.classList.remove('hidden');
};

window.addBulkTestTag = function(id, name) {
    document.getElementById('bulk-search-results').classList.add('hidden');
    document.getElementById('bulk-search-test').value = '';

    if (window.multipleAcceptanceSelectedTests.some(t => t.id === id)) return;
    window.multipleAcceptanceSelectedTests.push({ id, name });

    const container = document.getElementById('bulk-selected-tests-tags');
    container.innerHTML += `
        <span class="badge badge-info" id="bulk-tag-${id}" style="padding:6px 10px; font-size:0.8rem; display:flex; align-items:center; gap:6px; background-color: var(--primary); color:white;">
            ${name}
            <i data-lucide="x" style="width:12px; height:12px; cursor:pointer;" onclick="window.removeBulkTestTag(${id})"></i>
        </span>
    `;
    if (window.lucide) window.lucide.createIcons();
};

window.removeBulkTestTag = function(id) {
    window.multipleAcceptanceSelectedTests = window.multipleAcceptanceSelectedTests.filter(t => t.id !== id);
    const tag = document.getElementById(`bulk-tag-${id}`);
    if (tag) tag.remove();
};

window.saveMultipleAcceptance = async function() {
    if (!window.multipleAcceptancePatients || window.multipleAcceptancePatients.length === 0) return;
    if (window.multipleAcceptanceSelectedTests.length === 0) {
        alert("Errore: Selezionare almeno un esame LIS da associare ai pazienti.");
        return;
    }

    if (!confirm(`Eseguire l'accettazione massiva per ${window.multipleAcceptancePatients.length} pazienti?`)) return;

    const dbPatients = DB.get('patients') || [];
    const dbCompanies = DB.get('companies') || [];
    const medicalServices = DB.get('medical_services') || [];
    const priceListItems = DB.get('price_list_items') || [];
    const tubeTypes = DB.get('tube_types') || [];

    const bulkSessionUid = 'SESS-BULK-' + Date.now();

    for (const p of window.multipleAcceptancePatients) {
        let pat = dbPatients.find(item => item.tax_code === p.tax_code);
        if (!pat) {
            // create new patient
            const newPat = {
                last_name: p.last_name,
                first_name: p.first_name,
                tax_code: p.tax_code,
                gender: p.gender,
                birth_date: p.birth_date,
                email: p.email,
                phone: p.phone,
                company_id: p.company_id,
                uuid: 'PAT-' + Math.floor(Math.random()*90000)
            };
            pat = DB.insert('patients', newPat);
            dbPatients.push(pat);
        } else if (p.company_id && pat.company_id != p.company_id) {
            // update company link
            pat.company_id = p.company_id;
            DB.update('patients', pat.id, { company_id: p.company_id });
        }

        // LIS Sample Creation
        const servicesSelected = medicalServices.filter(s => window.multipleAcceptanceSelectedTests.some(t => t.id === s.id));
        const tubeType = servicesSelected[0]?.sample_type || "Sangue intero (EDTA - Viola)";
        const matchedTube = tubeTypes.find(t => t.name === tubeType);
        const tubeSuffix = matchedTube ? matchedTube.suffix : '000';
        const barcodeNum = window.getNextBarcode(tubeSuffix);

        const sample = {
            patient_id: pat.id,
            barcode: barcodeNum,
            sample_type: tubeType,
            status: 'da prelevare',
            session_uid: bulkSessionUid,
            bulk_session_uid: bulkSessionUid,
            collected_at: null,
            collected_by: null,
            report_notes: "",
            requesting_doctor: null
        };
        const newSam = DB.insert('lab_samples', sample);

        // LIS Tests creation
        servicesSelected.forEach(srv => {
            if (srv.parameters && srv.parameters.length > 0) {
                srv.parameters.forEach(param => {
                    const test = {
                        sample_id: newSam.id,
                        service_id: srv.id,
                        test_name: param.name,
                        result_value: null,
                        reference_range: param.reference_range || '',
                        unit: param.unit || '',
                        result_type: param.result_type || 'ALFABETICO',
                        status: 'pending',
                        verified_by: null,
                        verified_at: null
                    };
                    DB.insert('lab_tests', test);
                });
            } else {
                const test = {
                    sample_id: newSam.id,
                    service_id: srv.id,
                    test_name: srv.name,
                    result_value: null,
                    reference_range: srv.reference_range || '',
                    unit: srv.unit || '',
                    result_type: 'ALFABETICO',
                    status: 'pending',
                    verified_by: null,
                    verified_at: null
                };
                DB.insert('lab_tests', test);
            }
        });

        // Billing / Invoice Creation
        const company = dbCompanies.find(c => c.id == p.company_id);
        const listinoId = company ? company.price_list_id : 1;
        
        let subtotal = 0;
        servicesSelected.forEach(srv => {
            const item = priceListItems.find(pl => pl.price_list_id === listinoId && pl.service_id === srv.id);
            subtotal += Number(item ? item.price : (srv.price || 0)) || 0;
        });

        let stampDuty = subtotal > 77.47 ? 2.00 : 0.00;
        let amountDue = subtotal + stampDuty;

        const invoice = {
            admission_id: null,
            appointment_id: null,
            sample_id: newSam.id,
            study_id: null,
            invoice_number: getNextInvoiceNumber(),
            issue_date: new Date().toISOString().split('T')[0],
            subtotal: subtotal,
            discount_value: 0,
            discount_type: 'flat',
            discount_amount: 0,
            price_list_id: listinoId,
            claim_id: null,
            insurance_covered_amount: 0,
            stamp_duty: stampDuty,
            amount_due: amountDue,
            amount_paid: 0.0,
            payment_status: 'unpaid',
            payment_method: null,
            paid_at: null,
            is_insurance_invoice: false,
            company_id: company ? company.id : null,
            is_company_post: company && company.billing_type === 'company_post' ? 1 : 0
        };
        DB.insert('invoices', invoice);
        DB.logAudit(4, "ACCEPT_LIS_BOOKING_BULK", "lab_samples", newSam.id, { barcode: barcodeNum, session_uid: bulkSessionUid });
    }

    await DB.waitForSync();
    closeModal('modal-lis-multiple-acceptance');
    window.renderSamples();
    alert(`Importazione completata con successo! Inseriti ${window.multipleAcceptancePatients.length} pazienti ed emesse relative accettazioni in stato 'Da prelevare'.`);
};

// -------------------------------------------------------------
// LIS BULK MANAGE SUB-TAB FUNCTIONALITY
// -------------------------------------------------------------

window.toggleAllBulkSamples = function(chk) {
    const chks = document.querySelectorAll('.lis-bulk-sample-chk');
    chks.forEach(c => c.checked = chk.checked);
};

window.renderLisBulkManageView = function() {
    const select = document.getElementById('bulk-session-select');
    if (!select) return;

    select.innerHTML = '<option value="all">-- Tutte le Sessioni Attive --</option>';
    
    const samples = DB.get('lab_samples') || [];
    
    // Find all unique session uids that contain active "da prelevare" samples
    const activeSessions = [];
    samples.forEach(s => {
        if (s.status === 'da prelevare' && s.session_uid) {
            if (!activeSessions.includes(s.session_uid)) {
                activeSessions.push(s.session_uid);
            }
        }
    });

    activeSessions.forEach(uid => {
        const count = samples.filter(s => s.session_uid === uid && s.status === 'da prelevare').length;
        select.innerHTML += `<option value="${uid}">${uid} (${count} provette)</option>`;
    });

    window.loadBulkSessionSamples();
};

window.loadBulkSessionSamples = function() {
    const select = document.getElementById('bulk-session-select');
    const tbody = document.getElementById('bulk-samples-tbody');
    if (!select || !tbody) return;

    const selectedUid = select.value;
    const samples = DB.get('lab_samples') || [];
    const patients = DB.get('patients') || [];
    const tests = DB.get('lab_tests') || [];
    const services = DB.get('medical_services') || [];

    let filtered = samples.filter(s => s.status === 'da prelevare' || s.status === 'suspended');
    if (selectedUid !== 'all') {
        filtered = filtered.filter(s => s.session_uid === selectedUid);
    }

    tbody.innerHTML = '';
    if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Nessun campione da gestire trovato per questa sessione.</td></tr>';
        return;
    }

    filtered.forEach(s => {
        const p = patients.find(pat => pat.id === s.patient_id);
        const pName = p ? `${p.last_name.toUpperCase()} ${p.first_name}` : 'Paziente Sconosciuto';
        const samTests = tests.filter(t => t.sample_id === s.id);
        const testsStr = samTests.map(t => t.test_name).join(', ') || 'Analisi gen.';
        const statusBadge = s.status === 'suspended'
            ? '<span class="badge badge-danger" style="background-color:#ef4444;color:#fff;">SOSPESO</span>'
            : '<span class="badge" style="background-color:#64748b;color:#fff;">Da Prelevare</span>';

        tbody.innerHTML += `
            <tr>
                <td style="text-align: center;"><input type="checkbox" class="lis-bulk-sample-chk" value="${s.id}"></td>
                <td><strong>${s.barcode}</strong></td>
                <td>${pName}</td>
                <td>${s.sample_type}</td>
                <td><small>${testsStr}</small></td>
                <td>${statusBadge}</td>
            </tr>
        `;
    });
    if (window.lucide) window.lucide.createIcons();
};

window.bulkCollectSamples = async function() {
    const chks = document.querySelectorAll('.lis-bulk-sample-chk:checked');
    if (chks.length === 0) {
        alert("Seleziona almeno un campione da prelevare.");
        return;
    }

    const ids = Array.from(chks).map(c => parseInt(c.value));
    if (!confirm(`Effettuare il prelievo massivo di ${ids.length} campioni?`)) return;

    const loggedUser = JSON.parse(localStorage.getItem('nextcare_logged_in_user') || '{}');
    const staffId = loggedUser.id || 4;

    const samples = DB.get('lab_samples') || [];
    ids.forEach(id => {
        const samIdx = samples.findIndex(s => s.id === id);
        if (samIdx !== -1) {
            samples[samIdx].status = 'collected';
            samples[samIdx].collected_at = new Date().toISOString();
            samples[samIdx].collected_by = staffId;
            DB.logAudit(staffId, "PRELEVA_LIS_SAMPLE", "lab_samples", id, { bulk: true });
        }
    });

    DB.set('lab_samples', samples);
    await DB.waitForSync();

    window.renderLisBulkManageView();
    window.renderSamples();
    alert(`Prelievo completato per ${ids.length} campioni!`);
};

window.bulkSuspendSamples = async function() {
    const chks = document.querySelectorAll('.lis-bulk-sample-chk:checked');
    if (chks.length === 0) {
        alert("Seleziona almeno un campione da sospendere/ripristinare.");
        return;
    }

    const ids = Array.from(chks).map(c => parseInt(c.value));
    const samples = DB.get('lab_samples') || [];

    ids.forEach(id => {
        const samIdx = samples.findIndex(s => s.id === id);
        if (samIdx !== -1) {
            const current = samples[samIdx].status;
            samples[samIdx].status = (current === 'suspended') ? 'da prelevare' : 'suspended';
            DB.logAudit(4, "SAMPLE_SUSPEND_TOGGLE", "lab_samples", id, { previous_status: current });
        }
    });

    DB.set('lab_samples', samples);
    await DB.waitForSync();

    window.renderLisBulkManageView();
    window.renderSamples();
    alert(`Stato aggiornato per ${ids.length} campioni.`);
};

window.bulkPrintBarcodes = function() {
    const chks = document.querySelectorAll('.lis-bulk-sample-chk:checked');
    if (chks.length === 0) {
        alert("Seleziona almeno un campione per la stampa dei codici a barre.");
        return;
    }

    const ids = Array.from(chks).map(c => parseInt(c.value));
    const samples = DB.get('lab_samples') || [];
    const patients = DB.get('patients') || [];

    const printWin = window.open('', '_blank');
    if (!printWin) {
        alert("Abilita i pop-up per procedere alla stampa.");
        return;
    }

    let labelsHtml = '';
    ids.forEach(id => {
        const s = samples.find(sam => sam.id === id);
        const p = s ? patients.find(pat => pat.id === s.patient_id) : null;
        const pName = p ? `${p.last_name.toUpperCase()} ${p.first_name.substring(0,1)}.` : 'N/D';
        const barcodeVal = s ? s.barcode : '0000000000';
        const tubeType = s ? s.sample_type.split(' ')[0] : 'PROVETTA';

        labelsHtml += `
            <div style="width: 250px; height: 110px; border: 1px solid #000; border-radius: 4px; padding: 6px; box-sizing: border-box; text-align: center; font-family: monospace; display: inline-block; margin: 10px; vertical-align: top; background: white; color: black; line-height: 1.2;">
                <div style="font-size: 0.85rem; font-weight: bold; border-bottom: 1px solid #000; padding-bottom: 2px;">NEXTCARE CLINICAL LAB</div>
                <div style="font-size: 0.8rem; margin-top: 4px;"><strong>Paziente:</strong> ${pName}</div>
                <div style="font-size: 0.75rem;"><strong>Tipo:</strong> ${tubeType}</div>
                <div style="font-size: 0.95rem; font-weight: bold; margin-top: 4px; letter-spacing: 2px;">* ${barcodeVal} *</div>
                <div style="font-size: 0.7rem; color: #555;">Data: ${new Date().toLocaleDateString('it-IT')}</div>
            </div>
        `;
    });

    printWin.document.write(`
        <html>
        <head>
            <title>Stampa Etichette Provette</title>
            <style>
                body { background: white; padding: 20px; text-align: center; }
                @media print {
                    body { padding: 0; margin: 0; }
                }
            </style>
        </head>
        <body>
            <h2>Etichette Barcode per Provette Campioni</h2>
            <p>Applica sui contenitori LIS prima dell'invio allo strumento.</p>
            ${labelsHtml}
            <script>
                window.onload = function() {
                    window.print();
                    setTimeout(function() { window.close(); }, 500);
                }
            </script>
        </body>
        </html>
    `);
    printWin.document.close();
};

window.singlePrelevaSample = async function(sampleId) {
    if (typeof window.prelevaSample === 'function') {
        await window.prelevaSample(sampleId, true); // force single session bypass
        window.renderLisBulkManageView();
    }
};

// -------------------------------------------------------------
// MODULE 5: BUSINESS INTELLIGENCE DASHBOARD & CONVERSATIONAL AI
// -------------------------------------------------------------

window.renderBiDashboard = function() {
    const invoices = DB.get('invoices') || [];
    const admissions = DB.get('admissions') || [];
    const medicalServices = DB.get('medical_services') || [];
    const companies = DB.get('companies') || [];
    const labTests = DB.get('lab_tests') || [];
    const radStudies = DB.get('radiology_studies') || [];

    let totalProduction = 0; // sum of amount_due
    let totalRevenues = 0; // sum of amount_paid
    let totalPending = 0; // amount_due - amount_paid
    let volumeCount = 0; // total completed tests + studies + visits

    invoices.forEach(inv => {
        totalProduction += inv.amount_due || 0;
        totalRevenues += inv.amount_paid || 0;
        totalPending += (inv.amount_due - inv.amount_paid) || 0;
    });

    // Count clinical volume
    const activeTests = labTests.filter(t => t.status === 'verified' || t.status === 'completed');
    const activeRIS = radStudies.filter(s => s.status === 'completed');
    volumeCount = activeTests.length + activeRIS.length;

    // Set metrics
    document.getElementById('bi-metric-revenues').innerText = `€ ${totalRevenues.toLocaleString('it-IT', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    document.getElementById('bi-metric-pending').innerText = `€ ${totalPending.toLocaleString('it-IT', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
    document.getElementById('bi-metric-volume').innerText = volumeCount.toLocaleString('it-IT');

    // Aggregate monthly data for chart (pure JS/SVG renderer)
    const monthlyData = {};
    const monthsName = ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"];
    
    // Seed current and past months
    const curYear = new Date().getFullYear();
    for (let m = 0; m < 12; m++) {
        const key = `${curYear}-${String(m+1).padStart(2, '0')}`;
        monthlyData[key] = { name: monthsName[m], revenue: 0, production: 0 };
    }

    invoices.forEach(inv => {
        const date = inv.issue_date || '';
        if (date.startsWith(String(curYear))) {
            const key = date.substring(0, 7);
            if (monthlyData[key]) {
                monthlyData[key].revenue += inv.amount_paid || 0;
                monthlyData[key].production += inv.amount_due || 0;
            }
        }
    });

    const chartData = Object.values(monthlyData);
    window.renderBiSvgChart(chartData);

    // Percentage breakdown table: Profit Centers
    const pcData = {
        'SPECIALISTICA': 0,
        'IMAGING': 0,
        'LABORATORIO': 0
    };

    invoices.forEach(inv => {
        let type = 'SPECIALISTICA';
        if (inv.study_id) {
            const st = radStudies.find(s => s.id === inv.study_id);
            type = st && st.study_type === 'VISIT' ? 'SPECIALISTICA' : 'IMAGING';
        } else if (inv.sample_id) {
            type = 'LABORATORIO';
        }
        pcData[type] += inv.amount_due;
    });

    const tbody = document.querySelector('#bi-breakdown-table tbody');
    if (tbody) {
        tbody.innerHTML = '';
        const totalPc = Object.values(pcData).reduce((a, b) => a + b, 0) || 1;
        Object.entries(pcData).forEach(([pcName, val]) => {
            const pct = (val / totalPc) * 100;
            tbody.innerHTML += `
                <tr>
                    <td><strong>${pcName}</strong></td>
                    <td style="text-align: right;">€ ${val.toLocaleString('it-IT', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</td>
                    <td style="text-align: right;"><span class="badge badge-success" style="background-color:var(--primary);color:white;">${pct.toFixed(1)}%</span></td>
                </tr>
            `;
        });
    }
    if (window.lucide) window.lucide.createIcons();
};

window.renderBiSvgChart = function(data) {
    const container = document.getElementById('bi-chart-container');
    if (!container) return;

    const maxVal = Math.max(...data.map(d => Math.max(d.revenue, d.production))) || 1000;
    const height = 220;
    const width = 600;
    const padding = 40;

    let pointsProduction = '';
    let pointsRevenue = '';
    let xAxisLabels = '';
    let gridLines = '';

    const stepX = (width - padding * 2) / (data.length - 1 || 1);
    
    data.forEach((d, idx) => {
        const x = padding + idx * stepX;
        // production line y
        const yProd = height - padding - ((d.production / maxVal) * (height - padding * 2));
        // revenue line y
        const yRev = height - padding - ((d.revenue / maxVal) * (height - padding * 2));

        pointsProduction += `${x},${yProd} `;
        pointsRevenue += `${x},${yRev} `;

        xAxisLabels += `<text x="${x}" y="${height - 15}" font-size="10" fill="var(--text-secondary)" text-anchor="middle">${d.name}</text>`;
        gridLines += `<line x1="${x}" y1="${padding}" x2="${x}" y2="${height - padding}" stroke="var(--border-color)" stroke-dasharray="2,2"/>`;
    });

    // Y Axis labels
    let yAxisLabels = '';
    for (let i = 0; i <= 4; i++) {
        const val = (maxVal / 4) * i;
        const y = height - padding - (i * (height - padding * 2) / 4);
        yAxisLabels += `
            <text x="${padding - 8}" y="${y + 4}" font-size="9" fill="var(--text-secondary)" text-anchor="end">€ ${Math.round(val)}</text>
            <line x1="${padding}" y1="${y}" x2="${width - padding}" y2="${y}" stroke="var(--border-color)" stroke-width="0.5"/>
        `;
    }

    container.innerHTML = `
        <svg viewBox="0 0 ${width} ${height}" style="width: 100%; height: 100%; font-family: sans-serif;">
            <!-- Grid Lines -->
            ${gridLines}
            ${yAxisLabels}

            <!-- X Axis line -->
            <line x1="${padding}" y1="${height - padding}" x2="${width - padding}" y2="${height - padding}" stroke="var(--border-color)" stroke-width="2"/>

            <!-- Production Line (Blue) -->
            <polyline fill="none" stroke="#2563eb" stroke-width="3" points="${pointsProduction.trim()}"/>
            
            <!-- Revenue Line (Green) -->
            <polyline fill="none" stroke="#10b981" stroke-width="3" points="${pointsRevenue.trim()}"/>

            <!-- Labels -->
            ${xAxisLabels}

            <!-- Legend -->
            <g transform="translate(${width - 250}, 15)" font-size="10" font-weight="600">
                <rect x="0" y="0" width="12" height="12" fill="#2563eb" rx="2"/>
                <text x="16" y="10" fill="var(--text-primary)">Produzione (Fatturato Lordo)</text>
                <rect x="150" y="0" width="12" height="12" fill="#10b981" rx="2"/>
                <text x="166" y="10" fill="var(--text-primary)">Ricavi (Incassato)</text>
            </g>
        </svg>
    `;
};

window.handleBiChatSubmit = function(e) {
    if (e) e.preventDefault();
    const input = document.getElementById('bi-chat-input');
    const chatBox = document.getElementById('bi-chat-box');
    if (!input || !chatBox) return;

    const query = input.value.trim();
    if (!query) return;

    // Render User Message
    chatBox.innerHTML += `
        <div style="display: flex; gap: 8px; align-items: flex-start; justify-content: flex-end;">
            <div style="background: var(--primary-light); color: var(--primary); padding: 8px 12px; border-radius: 8px 0 8px 8px; max-width: 80%; line-height: 1.4;">
                ${query}
            </div>
            <div style="background: var(--primary-color); color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 700;">IO</div>
        </div>
    `;
    
    input.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    // Answer calculation (Direct local BI engine)
    setTimeout(() => {
        const response = window.computeBiAiResponse(query);
        chatBox.innerHTML += `
            <div style="display: flex; gap: 8px; align-items: flex-start;">
                <div style="background: var(--primary-color); color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; font-weight: 700;">AI</div>
                <div style="background: var(--bg-surface); border: 1px solid var(--border-color); padding: 8px 12px; border-radius: 0 8px 8px 8px; max-width: 80%; line-height: 1.4;">
                    ${response}
                </div>
            </div>
        `;
        chatBox.scrollTop = chatBox.scrollHeight;
    }, 600);
};

window.computeBiAiResponse = function(query) {
    const q = query.toLowerCase();
    
    const invoices = DB.get('invoices') || [];
    const companies = DB.get('companies') || [];
    const services = DB.get('medical_services') || [];
    const radStudies = DB.get('radiology_studies') || [];

    if (q.includes('profit') || q.includes('guadagn') || q.includes('esam') || q.includes('prestazion')) {
        // Calculate top profit services
        const serviceStats = {};
        invoices.forEach(inv => {
            let srvId = null;
            if (inv.study_id) {
                const st = radStudies.find(s => s.id === inv.study_id);
                if (st) srvId = st.service_id;
            } else if (inv.appointment_id) {
                const appSrvs = DB.get('appointment_services') || [];
                const matched = appSrvs.find(as => as.appointment_id === inv.appointment_id);
                if (matched) srvId = matched.service_id;
            }
            if (srvId) {
                if (!serviceStats[srvId]) serviceStats[srvId] = 0;
                serviceStats[srvId] += inv.amount_due;
            }
        });

        const sorted = Object.entries(serviceStats).sort((a,b) => b[1] - a[1]);
        let listHtml = 'Le prestazioni che hanno generato maggior fatturato sono:<br><ul>';
        sorted.slice(0, 3).forEach(([id, val]) => {
            const s = services.find(sv => sv.id == id);
            const name = s ? s.name : `Servizio #${id}`;
            listHtml += `<li><strong>${name}</strong>: € ${val.toFixed(2)}</li>`;
        });
        listHtml += '</ul>';
        return listHtml;
    }

    if (q.includes('aziend') || q.includes('convenzion')) {
        // Calculate breakdown by company
        const companyStats = {};
        invoices.forEach(inv => {
            if (inv.company_id) {
                if (!companyStats[inv.company_id]) companyStats[inv.company_id] = 0;
                companyStats[inv.company_id] += inv.amount_due;
            }
        });

        let listHtml = 'Ecco i ricavi lordi (fatturati) suddivisi per le aziende convenzionate:<br><ul>';
        Object.entries(companyStats).forEach(([id, val]) => {
            const c = companies.find(item => item.id == id);
            const name = c ? c.name : `Azienda #${id}`;
            listHtml += `<li><strong>${name}</strong>: € ${val.toFixed(2)}</li>`;
        });
        if (Object.keys(companyStats).length === 0) {
            listHtml += '<li>Nessuna transazione collegata ad aziende trovata al momento.</li>';
        }
        listHtml += '</ul>';
        return listHtml;
    }

    if (q.includes('insolvenz') || q.includes('sospes') || q.includes('non pagat')) {
        let unpaidSum = 0;
        let count = 0;
        invoices.forEach(inv => {
            if (inv.payment_status === 'unpaid') {
                unpaidSum += (inv.amount_due - inv.amount_paid);
                count++;
            }
        });

        return `Attualmente sono presenti <strong>${count} fatture in sospeso</strong> (non saldate), per un valore complessivo di <strong>€ ${unpaidSum.toFixed(2)}</strong>.<br><br><em>Suggerimento:</em> Controlla le aziende configurate come 'Fatturazione cumulativa post-hoc' nel menu HRIS & Turni per emettere fatture cumulative e saldare le pendenze.`;
    }

    // Default stats answer
    const totalProd = invoices.reduce((sum, inv) => sum + inv.amount_due, 0);
    const totalRev = invoices.reduce((sum, inv) => sum + inv.amount_paid, 0);
    return `Ecco un riepilogo generale delle performance di NextCare:<br>
    - <strong>Produzione totale (Fatturato Lordo):</strong> € ${totalProd.toFixed(2)}<br>
    - <strong>Ricavi totali (Incassato):</strong> € ${totalRev.toFixed(2)}<br>
    - <strong>Rapporto di Incasso:</strong> ${((totalRev / (totalProd || 1)) * 100).toFixed(1)}% delle prestazioni erogate.<br><br>
    Puoi chiedermi dettagli su aziende convenzionate, prestazioni o insolvenze scrivendo direttamente qui sopra.`;
};

// -------------------------------------------------------------
// EVENT LISTENERS & INTEGRATION OVERRIDES
// -------------------------------------------------------------

document.addEventListener('DOMContentLoaded', () => {
    // 1. Hook into tab switching to render BI Dashboard when active
    const oldSwitchTab = window.switchTab;
    window.switchTab = function(tabName) {
        if (typeof oldSwitchTab === 'function') oldSwitchTab(tabName);
        if (tabName === 'hris') {
            const activeHrisSub = document.querySelector('#tab-hris .sub-tabs-container .sub-tab-btn.active');
            if (activeHrisSub && activeHrisSub.id === 'sub-tab-hris-companies') {
                window.renderCompanies();
            }
        } else if (tabName === 'business-intelligence') {
            window.renderBiDashboard();
        }
    };

    // 2. Clone and intercept form submissions for MySQL sync validation
    const oldFormAdm = document.getElementById('form-add-admission');
    if (oldFormAdm) {
        const newFormAdm = oldFormAdm.cloneNode(true);
        oldFormAdm.parentNode.replaceChild(newFormAdm, oldFormAdm);
        newFormAdm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const patientId = parseInt(document.getElementById('adm-patient').value);
            const claimVal = document.getElementById('adm-claim').value;
            const companyIdVal = document.getElementById('adm-company').value;
            const companyId = companyIdVal ? parseInt(companyIdVal) : null;
            
            const admission = {
                patient_id: patientId,
                department: document.getElementById('adm-dept').value,
                reason: document.getElementById('adm-reason').value,
                admission_date: new Date().toISOString(),
                discharge_date: null,
                status: 'active',
                price_list_id: parseInt(document.getElementById('adm-listino').value || 1),
                claim_id: claimVal ? parseInt(claimVal) : null,
                discount_value: parseFloat(document.getElementById('adm-discount-val').value || 0),
                discount_type: document.getElementById('adm-discount-type').value || 'percentage',
                company_id: companyId
            };
            
            DB.insert('admissions', admission);
            
            if (companyId) {
                const patients = DB.get('patients') || [];
                const patientIdx = patients.findIndex(p => p.id === patientId);
                if (patientIdx !== -1) {
                    patients[patientIdx].company_id = companyId;
                    DB.set('patients', patients);
                }
            }
            
            await DB.waitForSync();
            closeModal('modal-add-admission');
            newFormAdm.reset();
            if (typeof renderAdmissionsAndInvoices === 'function') renderAdmissionsAndInvoices();
            alert("Ricovero registrato con successo!");
        });
    }

    const oldFormDicom = document.getElementById('form-dicom-report');
    if (oldFormDicom) {
        const newFormDicom = oldFormDicom.cloneNode(true);
        oldFormDicom.parentNode.replaceChild(newFormDicom, oldFormDicom);
        newFormDicom.addEventListener('submit', async (e) => {
            e.preventDefault();
            const studyId = parseInt(document.getElementById('dicom-study-id').value);
            const reportHTML = document.getElementById('dicom-report-editor').innerHTML;
            const radId = parseInt(document.getElementById('dicom-radiologist').value);
            
            if (!reportHTML.trim() || reportHTML === '<br>' || reportHTML === 'Scrivi qui il referto radiologico dell\'esame eseguito...') {
                alert("Inserire il testo del referto prima di firmare!");
                return;
            }

            const study = DB.get('radiology_studies').find(s => s.id === studyId);
            const isVisit = study && study.study_type === 'VISIT';

            const doseInput = document.getElementById('dicom-dose-value');
            let doseVal = null;
            if (doseInput && doseInput.value.trim() !== '' && !isVisit) {
                doseVal = parseFloat(doseInput.value);
                if (isNaN(doseVal)) {
                    doseVal = null;
                }
            }

            const updatedStudy = DB.update('radiology_studies', studyId, {
                report_text: reportHTML,
                signed_by: radId,
                signed_at: new Date().toISOString(),
                status: 'completed',
                dose_value_msv: doseVal
            });
            
            DB.logAudit(radId, "RIS_REPORT_SIGN", "radiology_studies", studyId, { signed_by: radId });
            
            const patient = DB.get('patients').find(p => p.id === updatedStudy.patient_id);
            if (patient) {
                const srv = DB.get('medical_services').find(s => s.id === updatedStudy.service_id);
                const srvName = srv ? srv.name : updatedStudy.study_type;
                const docStaff = DB.get('staff').find(s => s.id === radId);
                const docName = docStaff ? `Firmato digitalmente da Dott. ${docStaff.last_name}` : 'Firmato digitalmente';
                
                if (typeof sendSimulatedEmail === 'function') {
                    sendSimulatedEmail(patient.id, 'report_ready', {
                        paziente: `${patient.first_name} ${patient.last_name}`,
                        data: new Date(updatedStudy.signed_at).toLocaleDateString('it-IT'),
                        prestazione: srvName,
                        dettaglio: docName
                    });
                }
            }

            await DB.waitForSync();
            closeModal('modal-dicom-viewer');
            if (typeof renderRisStudies === 'function') renderRisStudies();
            alert("Referto firmato digitalmente e archiviato con successo!");
        });
    }

    const oldFormCheckin = document.getElementById('form-checkin-appointment');
    if (oldFormCheckin) {
        const newFormCheckin = oldFormCheckin.cloneNode(true);
        oldFormCheckin.parentNode.replaceChild(newFormCheckin, oldFormCheckin);
        newFormCheckin.addEventListener('submit', async (e) => {
            e.preventDefault();
            const appId = parseInt(document.getElementById('checkin-app-id').value);
            const listinoId = parseInt(document.getElementById('checkin-listino').value);
            const claimIdVal = document.getElementById('checkin-claim').value;
            const discountVal = parseFloat(document.getElementById('checkin-discount-val').value || 0);
            const discountType = document.getElementById('checkin-discount-type').value;
            const requestingDoctorVal = (document.getElementById('checkin-requester')?.value || '').trim();
            const resDoc = window.resolveDoctorFromName(requestingDoctorVal);

            const appointments = DB.get('appointments') || [];
            const app = appointments.find(a => a.id === appId);
            if (!app) return;

            const companyIdVal = document.getElementById('checkin-company').value;
            const companyId = companyIdVal ? parseInt(companyIdVal) : null;
            const companies = DB.get('companies') || [];
            const company = companies.find(c => c.id == companyId);

            DB.update('appointments', appId, {
                doctor_id: resDoc.doctor_id || app.doctor_id,
                requesting_doctor: resDoc.requesting_doctor || null
            });

            const appServices = DB.get('appointment_services') || [];
            const services = DB.get('medical_services') || [];
            const priceListItems = DB.get('price_list_items') || [];
            const patients = DB.get('patients');

            const patient = patients.find(p => p.id === app.patient_id);
            const serviceIds = appServices.filter(as => as.appointment_id === appId).map(as => as.service_id);
            const bookedServices = services.filter(sv => serviceIds.includes(sv.id));

            if (bookedServices.length === 0) {
                alert("Errore: Nessuna prestazione associata a questa prenotazione.");
                return;
            }

            const explodedServiceIds = window.expandServices(serviceIds);
            const executionServices = services.filter(sv => explodedServiceIds.includes(sv.id));

            const lisServices = executionServices.filter(s => s.type === 'lis');
            const risServices = executionServices.filter(s => s.type === 'ris');
            const visitServices = executionServices.filter(s => s.type === 'visita');

            let tsrmId = null;
            if (risServices.length > 0) {
                const tsrmIdVal = document.getElementById('checkin-tsrm').value;
                if (!tsrmIdVal) {
                    alert("Errore: Selezionare un tecnico TSRM prima di procedere con l'accettazione RIS.");
                    return;
                }
                tsrmId = parseInt(tsrmIdVal);
            }

            let subtotal = 0;
            const customRates = {};
            const inputs = document.querySelectorAll('#checkin-services-list .checkin-price-input');
            inputs.forEach(input => {
                const srvId = parseInt(input.dataset.serviceId);
                const price = parseFloat(input.value || 0) || 0;
                customRates[srvId] = price;
                subtotal += price;
            });

            let discountAmt = 0;
            if (discountType === 'percentage') {
                discountAmt = subtotal * (discountVal / 100);
            } else {
                discountAmt = discountVal;
            }
            discountAmt = Math.min(discountAmt, subtotal);
            const discountedTotal = subtotal - discountAmt;

            let insuranceCovered = 0;
            let patientTotal = discountedTotal;
            if (claimIdVal) {
                const claim = DB.get('patient_claims').find(c => c.id === parseInt(claimIdVal));
                if (claim) {
                    if (claim.deductible_type === 'percentage') {
                        patientTotal = discountedTotal * (claim.deductible_value / 100);
                        insuranceCovered = discountedTotal - patientTotal;
                    } else {
                        patientTotal = Math.min(discountedTotal, claim.deductible_value);
                        insuranceCovered = discountedTotal - patientTotal;
                    }
                }
            }

            let createdSample = null;
            let createdStudyIds = [];

            if (lisServices.length > 0) {
                const tubeType = lisServices[0].sample_type || "Sangue intero (EDTA - Viola)";
                const tubeTypes = DB.get('tube_types') || [];
                const matchedTube = tubeTypes.find(t => t.name === tubeType);
                const tubeSuffix = matchedTube ? matchedTube.suffix : '000';
                const barcodeNum = window.getNextBarcode(tubeSuffix);
                const sessionUid = 'SESS-LIS-' + app.patient_id + '-' + Date.now();
                
                const sample = {
                    patient_id: app.patient_id,
                    barcode: barcodeNum,
                    sample_type: tubeType,
                    status: 'da prelevare',
                    session_uid: sessionUid,
                    collected_at: null,
                    collected_by: null,
                    report_notes: "",
                    requesting_doctor: resDoc.requesting_doctor || null
                };
                createdSample = DB.insert('lab_samples', sample);
                
                lisServices.forEach(srv => {
                    if (srv.parameters && srv.parameters.length > 0) {
                        srv.parameters.forEach(p => {
                            const test = {
                                sample_id: createdSample.id,
                                service_id: srv.id,
                                test_name: p.name,
                                result_value: null,
                                reference_range: p.reference_range || '',
                                unit: p.unit || '',
                                result_type: p.result_type || 'ALFABETICO',
                                status: 'pending',
                                verified_by: null,
                                verified_at: null
                            };
                            DB.insert('lab_tests', test);
                        });
                    } else {
                        const test = {
                            sample_id: createdSample.id,
                            service_id: srv.id,
                            test_name: srv.name,
                            result_value: null,
                            reference_range: srv.reference_range || '',
                            unit: srv.unit || '',
                            result_type: 'ALFABETICO',
                            status: 'pending',
                            verified_by: null,
                            verified_at: null
                        };
                        DB.insert('lab_tests', test);
                    }
                });
                DB.logAudit(4, "ACCEPT_LIS_BOOKING", "lab_samples", createdSample.id, { barcode: barcodeNum, tests: lisServices.length });
            }

            if (risServices.length > 0) {
                risServices.forEach(srv => {
                    let studyType = 'XRAY';
                    if (srv.name.toLowerCase().includes('risonanza') || srv.name.toLowerCase().includes('mri')) studyType = 'MRI';
                    else if (srv.name.toLowerCase().includes('tac') || srv.name.toLowerCase().includes('computerizzata')) studyType = 'CT';
                    else if (srv.name.toLowerCase().includes('eco')) studyType = 'ULTRASOUND';

                    const study = {
                        patient_id: app.patient_id,
                        doctor_id: resDoc.doctor_id || app.doctor_id || 2,
                        service_id: srv.id,
                        study_type: studyType,
                        scheduled_at: app.appointment_datetime,
                        status: 'scheduled',
                        dicom_series_uid: '1.2.840.113619.2.' + Math.floor(Math.random()*9000) + '.' + Math.floor(Math.random()*900),
                        report_text: null,
                        signed_by: null,
                        signed_at: null,
                        tsrm_id: tsrmId,
                        requesting_doctor: resDoc.requesting_doctor || null
                    };
                    const newStudy = DB.insert('radiology_studies', study);
                    createdStudyIds.push(newStudy.id);
                    DB.logAudit(6, "ACCEPT_RIS_BOOKING", "radiology_studies", newStudy.id, { type: studyType, tsrm_id: tsrmId });
                });
            }

            if (visitServices.length > 0) {
                visitServices.forEach(srv => {
                    const study = {
                        patient_id: app.patient_id,
                        doctor_id: app.doctor_id || 2,
                        service_id: srv.id,
                        study_type: 'VISIT',
                        scheduled_at: app.appointment_datetime,
                        status: 'in_progress',
                        dicom_series_uid: '1.2.840.113619.2.' + Math.floor(Math.random()*9000) + '.' + Math.floor(Math.random()*900),
                        report_text: null,
                        signed_by: null,
                        signed_at: null
                    };
                    const newStudy = DB.insert('radiology_studies', study);
                    createdStudyIds.push(newStudy.id);
                    DB.logAudit(6, "ACCEPT_VISIT_BOOKING", "radiology_studies", newStudy.id, { type: 'VISIT' });
                });
            }

            DB.update('appointments', appId, { status: 'completed' });

            // Update patient company link
            if (companyId) {
                const patientsList = DB.get('patients') || [];
                const patIdx = patientsList.findIndex(item => item.id == app.patient_id);
                if (patIdx !== -1) {
                    patientsList[patIdx].company_id = companyId;
                    DB.set('patients', patientsList);
                }
            }

            // Billing
            let finalAmountToPay = 0;
            let createdInvoiceId = null;
            if (subtotal > 0) {
                const invoiceNum = getNextInvoiceNumber();
                let stampDuty = patientTotal > 77.47 ? 2.00 : 0.00;
                let amountDue = patientTotal + stampDuty;
                
                const invoice = {
                    admission_id: null,
                    appointment_id: appId,
                    sample_id: createdSample ? createdSample.id : null,
                    study_id: createdStudyIds.length > 0 ? createdStudyIds[0] : null,
                    invoice_number: invoiceNum,
                    issue_date: new Date().toISOString().split('T')[0],
                    subtotal: subtotal,
                    discount_value: discountVal,
                    discount_type: discountType,
                    discount_amount: discountAmt,
                    price_list_id: listinoId,
                    claim_id: claimIdVal ? parseInt(claimIdVal) : null,
                    insurance_covered_amount: insuranceCovered,
                    stamp_duty: stampDuty,
                    amount_due: amountDue,
                    amount_paid: 0.0,
                    payment_status: 'unpaid',
                    payment_method: null,
                    paid_at: null,
                    is_insurance_invoice: false,
                    custom_rates: customRates,
                    company_id: companyId,
                    is_company_post: company && company.billing_type === 'company_post' ? 1 : 0
                };
                const insertedInv = DB.insert('invoices', invoice);
                createdInvoiceId = insertedInv.id;
                DB.logAudit(6, "AUTO_BILL_EMITTED", "invoices", null, { invoice_number: invoiceNum, amount: amountDue });
                finalAmountToPay = amountDue;
            }

            await DB.waitForSync();
            closeModal('modal-checkin-appointment');

            alert(`Accettazione completata con successo! \n\n- Prenotazione registrata. \n\n${createdSample ? `- Campione LIS creato con Barcode: ${createdSample.barcode} \n\n` : ''}${createdStudyIds.length > 0 ? `- Generati ${createdStudyIds.length} studi/visite in elaborazione. \n\n` : ''}- Emessa fattura non pagata di € ${finalAmountToPay.toFixed(2)} (incluso bollo se applicabile).`);

            if (typeof renderAppointments === 'function') renderAppointments();
            if (typeof renderSamples === 'function') renderSamples();
            if (typeof renderRisStudies === 'function') renderRisStudies();
            if (typeof renderAdmissionsAndInvoices === 'function') renderAdmissionsAndInvoices();
            if (typeof window.populateRequesterDatalist === 'function') window.populateRequesterDatalist();

            // Evaluate consents
            const requiredTemplates = window.evaluateRequiredConsents(app.patient_id, explodedServiceIds, resDoc.doctor_id || app.doctor_id);
            if (requiredTemplates.length > 0) {
                window.lastCheckoutConsents = requiredTemplates;
                window.lastCheckoutPatientId = app.patient_id;
                window.lastCheckoutServiceIds = explodedServiceIds;
                window.lastCheckoutDoctorId = resDoc.doctor_id || app.doctor_id;
                
                const listEl = document.getElementById('print-consents-list');
                if (listEl) {
                    listEl.innerHTML = '';
                    requiredTemplates.forEach(tpl => {
                        let ruleDesc = "Generico";
                        if (tpl.scope === 'by_modality') ruleDesc = `Branca: ${tpl.modality}`;
                        else if (tpl.scope === 'by_doctor') ruleDesc = "Specifico per Medico";
                        else if (tpl.scope === 'gender_age') ruleDesc = `Donne Fertili (${tpl.min_age}-${tpl.max_age} anni)`;
                        listEl.innerHTML += `<div style="padding:6px 12px;background:var(--bg-base);border-radius:4px;border:1px solid var(--border-color);font-size:0.8rem;margin-bottom:4px;"><strong>${tpl.title}</strong> (${ruleDesc})</div>`;
                    });
                }
                openModal('modal-print-consents');
            }
        });
    }
});

// -------------------------------------------------------------
// SIDEBAR HISTORY LOADER (RIS/LIS/CUP HISTORY SIDE PANEL)
// -------------------------------------------------------------

window.openDicomViewer = function(studyId, isEdit = false) {
    const studies = DB.get('radiology_studies') || [];
    const patients = DB.get('patients') || [];
    const staff = DB.get('staff') || [];
    const services = DB.get('medical_services') || [];
    
    const study = studies.find(s => s.id === studyId);
    if (!study) return;
    const p = patients.find(pat => pat.id === study.patient_id);
    const srv = services.find(sv => sv.id === study.service_id);
    
    document.getElementById('dicom-study-id').value = studyId;
    document.getElementById('dicom-pat-id').innerText = p.uuid ? p.uuid.substring(0,8).toUpperCase() : 'N/D';
    document.getElementById('dicom-pat-name').innerText = `${p.last_name.toUpperCase()} ${p.first_name.toUpperCase()}`;
    document.getElementById('dicom-study-type').innerText = srv ? srv.name : study.study_type;
    
    const isVisit = study.study_type === 'VISIT';
    const layout = document.querySelector('.dicom-layout');
    if (isVisit) {
        layout.classList.add('no-viewer');
        document.getElementById('dicom-modal-title').innerText = "NextCare Refertazione Visita Specialistica";
        document.getElementById('dicom-radiologist-label').innerText = "Specialista Refertatore *";
        document.getElementById('dicom-report-label').innerText = "Referto Visita Specialistica (WYSIWYG) *";
        document.getElementById('dicom-report-editor').setAttribute('placeholder', "Scrivi qui il referto della visita specialistica...");
    } else {
        layout.classList.remove('no-viewer');
        document.getElementById('dicom-modal-title').innerText = "NextCare Reporting Specialistico RIS";
        document.getElementById('dicom-radiologist-label').innerText = "Radiologo Refertatore *";
        document.getElementById('dicom-report-label').innerText = "Referto Radiologico Clinico (WYSIWYG) *";
        document.getElementById('dicom-report-editor').setAttribute('placeholder', "Scrivi qui il referto radiologico dell'esame eseguito...");
    }

    const radSelect = document.getElementById('dicom-radiologist');
    radSelect.innerHTML = isVisit ? '<option value="">-- Seleziona Medico --</option>' : '<option value="">-- Seleziona Radiologo --</option>';
    staff.filter(s => s.role === 'doctor').forEach(st => {
        radSelect.innerHTML += `<option value="${st.id}">Dott. ${st.last_name}</option>`;
    });
    
    const reportEditor = document.getElementById('dicom-report-editor');
    const toolbar = document.getElementById('ris-editor-toolbar');
    const submitBtn = document.getElementById('btn-dicom-report-submit');
    
    // TSRM Operator & diagnostic query display
    const queryContainer = document.getElementById('dicom-clinical-query-container');
    const queryTextEl = document.getElementById('dicom-clinical-query-text');
    const queryAttachEl = document.getElementById('dicom-clinical-query-attachment');
    const attachLabel = document.getElementById('lbl-dicom-attachment-name');
    const tsrmNameEl = document.getElementById('dicom-tsrm-name');
    const execDateEl = document.getElementById('dicom-execution-date');

    const tsrmStaff = staff.find(st => st.id === study.tsrm_id);
    if (tsrmNameEl) tsrmNameEl.innerText = tsrmStaff ? `${tsrmStaff.last_name} ${tsrmStaff.first_name}` : 'N/D';
    if (execDateEl) execDateEl.innerText = study.scheduled_at ? new Date(study.scheduled_at).toLocaleDateString('it-IT') : 'N/D';
    
    if (queryContainer) {
        if (study.clinical_query || study.attachment_name) {
            queryContainer.style.display = 'block';
            queryTextEl.innerHTML = study.clinical_query || '<i>Nessun quesito diagnostico digitato.</i>';
            if (study.attachment_name) {
                queryAttachEl.style.display = 'block';
                attachLabel.innerText = study.attachment_name;
            } else {
                queryAttachEl.style.display = 'none';
            }
        } else {
            queryContainer.style.display = 'none';
        }
    }
    
    const disableFields = (study.status === 'completed' && !isEdit);
    
    if (disableFields) {
        reportEditor.innerHTML = study.report_text;
        reportEditor.contentEditable = "false";
        radSelect.value = study.signed_by;
        radSelect.disabled = true;
        toolbar.style.display = "none";
        submitBtn.style.display = 'none';
    } else {
        reportEditor.innerHTML = study.report_text || '';
        reportEditor.contentEditable = "true";
        radSelect.value = study.signed_by || '';
        radSelect.disabled = false;
        toolbar.style.display = "flex";
        submitBtn.style.display = 'block';
        submitBtn.innerText = study.status === 'completed' ? "Salva Modifiche" : "Firma Digitale & Archivia";
    }

    // Populate templates dropdown
    window.handleRisRadiologistChange();

    // Unified Clinical History Sidebar (RIS + LIS + CUP)
    const historyList = document.getElementById('ris-history-list');
    if (historyList) {
        historyList.innerHTML = '';
        const historyItems = [];

        // 1. Completed RIS Studies
        const pastRIS = studies.filter(s => s.patient_id === study.patient_id && s.status === 'completed' && s.id !== studyId);
        pastRIS.forEach(s => {
            const srvObj = services.find(sv => sv.id === s.service_id);
            const sName = srvObj ? srvObj.name : s.study_type;
            const reporter = staff.find(st => st.id === s.signed_by);
            const rName = reporter ? `Dr. ${reporter.last_name}` : 'Specialista';

            historyItems.push({
                date: new Date(s.signed_at || s.scheduled_at),
                type: 'RIS',
                title: sName,
                meta: `${rName} - RIS Radiologia`,
                content: s.report_text,
                attachment: s.attachment_name,
                id: s.id
            });
        });

        // 2. Completed LIS Reports
        const labReports = DB.get('lab_reports') || [];
        const labSamples = DB.get('lab_samples') || [];
        const labTests = DB.get('lab_tests') || [];
        const patSamples = labSamples.filter(s => s.patient_id === study.patient_id && s.status === 'completed');
        
        patSamples.forEach(sam => {
            const samTests = labTests.filter(t => t.sample_id === sam.id);
            let testRowsHtml = '<table style="width:100%; border-collapse:collapse; font-size:0.75rem; margin-top:5px;">';
            samTests.forEach(t => {
                testRowsHtml += `<tr><td style="padding:2px 4px; border-bottom:1px solid var(--border-color);">${t.test_name}</td><td style="padding:2px 4px; border-bottom:1px solid var(--border-color); font-weight:bold; text-align:right;">${t.result_value || 'N/D'} ${t.unit || ''}</td></tr>`;
            });
            testRowsHtml += '</table>';

            historyItems.push({
                date: new Date(sam.collected_at || sam.created_at),
                type: 'LIS',
                title: `Analisi di Laboratorio`,
                meta: `Sessione: ${sam.session_uid || 'N/D'} - LIS`,
                content: testRowsHtml
            });
        });

        // 3. Completed CUP Visite
        const appointments = DB.get('appointments') || [];
        const pastCUP = appointments.filter(a => a.patient_id === study.patient_id && a.status === 'completed');
        pastCUP.forEach(app => {
            const doc = staff.find(s => s.id === app.doctor_id);
            const docName = doc ? `Dr. ${doc.last_name}` : 'Medico';
            historyItems.push({
                date: new Date(app.appointment_datetime),
                type: 'CUP',
                title: `Visita Specialistica`,
                meta: `${docName} - CUP`,
                content: `<p><b>Note di Accettazione:</b> ${app.notes || 'Nessuna nota aggiuntiva.'}</p>`
            });
        });

        // Sort chronological descending
        historyItems.sort((a, b) => b.date - a.date);

        if (historyItems.length === 0) {
            historyList.innerHTML = '<span class="text-muted" style="font-size:0.75rem;">Nessun referto storico presente.</span>';
        } else {
            historyItems.forEach(item => {
                const sDate = item.date.toLocaleDateString('it-IT');
                const div = document.createElement('div');
                div.style.background = 'var(--bg-surface)';
                div.style.border = '1px solid var(--border-color)';
                div.style.borderRadius = 'var(--radius-sm)';
                div.style.padding = '8px';
                div.style.fontSize = '0.8rem';
                div.style.marginBottom = '6px';

                let iconName = 'file-text';
                let iconColor = 'var(--primary)';
                if (item.type === 'LIS') { iconName = 'droplet'; iconColor = 'var(--warning)'; }
                else if (item.type === 'CUP') { iconName = 'calendar'; iconColor = 'var(--success)'; }

                div.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:center; cursor:pointer;" onclick="this.nextElementSibling.style.display = this.nextElementSibling.style.display === 'none' ? 'block' : 'none'">
                        <div>
                            <span style="display:inline-flex; align-items:center; gap:4px; font-weight:700; color:${iconColor}">
                                <i data-lucide="${iconName}" style="width:12px; height:12px;"></i> ${item.title}
                            </span><br>
                            <span style="font-size:0.7rem; color:var(--text-secondary);">${sDate} - ${item.meta}</span>
                        </div>
                        <i data-lucide="chevron-down" style="width:14px; height:14px; color:var(--text-secondary);"></i>
                    </div>
                    <div style="display:none; margin-top:8px; border-top:1px dashed var(--border-color); padding-top:6px; font-size:0.75rem; color:var(--text-main); max-height:180px; overflow-y:auto;">
                        ${item.content}
                    </div>
                `;
                historyList.appendChild(div);
            });
            if (window.lucide) window.lucide.createIcons();
        }
    }

    const doseGroup = document.getElementById('dicom-dose-value')?.closest('.form-group');
    if (doseGroup) {
        doseGroup.style.display = isVisit ? 'none' : 'block';
    }
    const doseInput = document.getElementById('dicom-dose-value');
    const doseIndicator = document.getElementById('dicom-dose-class-indicator');
    if (doseInput && doseIndicator) {
        const updateIndicator = () => {
            const val = parseFloat(doseInput.value);
            if (isNaN(val) || val === null || doseInput.value === '') {
                doseIndicator.innerText = '';
                return;
            }
            let text = '';
            if (val === 0) text = "Classe 0 (0 mSv) - Ecografia, Risonanza Magnetica (senza radiazioni)";
            else if (val < 1) text = "Classe I (< 1 mSv) - RX Torace, RX arti";
            else if (val < 5) text = "Classe II (1 - 5 mSv) - RX addome, TC cranio";
            else if (val <= 10) text = "Classe III (5 - 10 mSv) - TC torace, TC addome";
            else text = "Classe IV (> 10 mSv) - TC addome-bacino o procedure interventistiche";
            doseIndicator.innerText = `Classe Dose stimata: ${text}`;
        };
        
        const newDoseInput = doseInput.cloneNode(true);
        doseInput.parentNode.replaceChild(newDoseInput, doseInput);
        newDoseInput.addEventListener('input', updateIndicator);
        newDoseInput.value = (study.dose_value_msv !== undefined && study.dose_value_msv !== null) ? study.dose_value_msv : '';
        updateIndicator();

        if (disableFields) {
            newDoseInput.disabled = true;
        } else {
            newDoseInput.disabled = false;
        }
    }

    openModal('modal-dicom-viewer');
};

// Override original bulkPrintLisReports to support company names on reports
window.bulkPrintLisReports = function() {
    if (!window.selectedReportingSessionUids || window.selectedReportingSessionUids.length === 0) {
        alert("Seleziona almeno un'accettazione da stampare.");
        return;
    }

    const samples = DB.get('lab_samples') || [];
    const patients = DB.get('patients') || [];
    const tests = DB.get('lab_tests') || [];
    const reports = DB.get('lab_reports') || [];
    const staff = DB.get('staff') || [];
    const services = DB.get('medical_services') || [];
    const companies = DB.get('companies') || [];

    let printHtml = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Stampa Referti LIS</title>
            <style>
                body { font-family: 'Segoe UI', Roboto, sans-serif; color: #333; margin: 20px; line-height: 1.4; }
                .report-page { max-width: 800px; margin: 0 auto 40px auto; border: 1px solid #ddd; padding: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); position: relative; }
                .report-header { display: flex; justify-content: space-between; border-bottom: 2px solid #2563eb; padding-bottom: 15px; margin-bottom: 20px; }
                .logo-section h1 { margin: 0; color: #2563eb; font-size: 1.6rem; }
                .logo-section p { margin: 2px 0 0 0; font-size: 0.8rem; color: #666; }
                .meta-section { text-align: right; font-size: 0.85rem; color: #444; }
                .patient-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 15px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 25px; font-size: 0.9rem; }
                .patient-box div strong { color: #475569; }
                .section-title { font-size: 1.1rem; font-weight: bold; color: #1e3a8a; border-bottom: 1px solid #cbd5e1; padding-bottom: 5px; margin-top: 20px; margin-bottom: 10px; }
                table { width: 100%; border-collapse: collapse; margin-bottom: 20px; font-size: 0.88rem; }
                th { background-color: #f1f5f9; text-align: left; padding: 8px 10px; border-bottom: 2px solid #cbd5e1; color: #475569; }
                td { padding: 8px 10px; border-bottom: 1px solid #e2e8f0; }
                .flag-normal { color: #16a34a; font-weight: 600; }
                .flag-out { color: #dc2626; font-weight: bold; background-color: #fef2f2; padding: 2px 6px; border-radius: 4px; }
                .report-footer { border-top: 1px solid #cbd5e1; padding-top: 15px; margin-top: 30px; display: flex; justify-content: space-between; font-size: 0.8rem; color: #666; }
                .watermark { position: absolute; top: 40%; left: 10%; right: 10%; transform: rotate(-30deg); font-size: 5rem; color: rgba(239, 68, 68, 0.08); font-weight: 900; text-transform: uppercase; text-align: center; pointer-events: none; }
                .watermark-official { color: rgba(16, 185, 129, 0.06); }
                @media print {
                    body { margin: 0; }
                    .report-page { border: none; padding: 0; box-shadow: none; page-break-after: always; max-width: 100%; }
                    .report-page:last-child { page-break-after: avoid; }
                }
            </style>
        </head>
        <body>
    `;

    window.selectedReportingSessionUids.forEach(uid => {
        const sessionSamples = samples.filter(s => s.session_uid === uid);
        if (sessionSamples.length === 0) return;
        
        const firstSample = sessionSamples[0];
        const pat = patients.find(p => p.id === firstSample.patient_id) || {};
        const rep = reports.find(r => r.session_uid === uid);
        const repStatus = rep?.status || 'preliminary';
        const repNotes = rep?.notes || 'Nessuna nota aggiuntiva.';

        const patName = `${pat.last_name || ''} ${pat.first_name || ''}`;
        const patGender = pat.gender || 'N/D';
        const patBirth = pat.birth_date ? new Date(pat.birth_date).toLocaleDateString('it-IT') : 'N/D';
        const patTax = pat.tax_code || 'N/D';

        const company = pat.company_id ? companies.find(c => c.id == pat.company_id) : null;
        const companyName = company ? company.name : '';

        const sampleIds = sessionSamples.map(s => s.id);
        const sessionTests = tests.filter(t => sampleIds.includes(t.sample_id));

        const collectedDate = firstSample.collected_at ? new Date(firstSample.collected_at).toLocaleString('it-IT') : '-';
        const printedDate = new Date().toLocaleString('it-IT');

        const watermarkText = repStatus === 'official' ? 'REFERTO UFFICIALE' : 'BOZZA PRELIMINARE';
        const watermarkClass = repStatus === 'official' ? 'watermark-official' : '';

        printHtml += `
            <div class="report-page">
                <div class="watermark ${watermarkClass}">${watermarkText}</div>
                <div class="report-header">
                    <div class="logo-section">
                        <h1>NextCare Health Systems</h1>
                        <p>Digital Health Clinic - Laboratorio Analisi Cliniche</p>
                    </div>
                    <div class="meta-section">
                        <strong>ID Sessione:</strong> ${uid}<br>
                        <strong>Data Accettazione:</strong> ${collectedDate}<br>
                        <strong>Data Stampa:</strong> ${printedDate}
                    </div>
                </div>
                <div class="patient-box">
                    <div><strong>Cognome e Nome:</strong> ${patName}</div>
                    <div><strong>Codice Fiscale:</strong> ${patTax}</div>
                    <div><strong>Data di Nascita:</strong> ${patBirth}</div>
                    <div><strong>Genere:</strong> ${patGender}</div>
                    ${companyName ? `<div style="grid-column: 1 / -1;"><strong>Convenzione Azienda:</strong> ${companyName.toUpperCase()}</div>` : ''}
                </div>

                <div class="section-title">RISULTATI ANALISI DI LABORATORIO</div>
                <table>
                    <thead>
                        <tr>
                            <th>Esame / Parametro</th>
                            <th style="text-align: center;">Risultato</th>
                            <th>Unità</th>
                            <th>Valori di Riferimento</th>
                            <th style="text-align: center;">Stato</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        if (sessionTests.length === 0) {
            printHtml += `<tr><td colspan="5" style="text-align:center;">Nessun risultato disponibile.</td></tr>`;
        } else {
            const groups = {};
            sessionTests.forEach(t => {
                let key = t.service_id;
                if (!key) {
                    if (t.test_name.startsWith('Emocromo (')) {
                        const s = services.find(srv => srv.name.toLowerCase().includes('emocromo'));
                        key = s ? s.id : 'emocromo';
                    } else if (t.test_name.startsWith('Elettroforesi (')) {
                        const s = services.find(srv => srv.name.toLowerCase().includes('elettroforesi'));
                        key = s ? s.id : 'elettroforesi';
                    } else if (t.test_name.startsWith('Esame Urine (')) {
                        const s = services.find(srv => srv.name.toLowerCase().includes('urine'));
                        key = s ? s.id : 'urine';
                    } else {
                        key = t.test_name;
                    }
                }
                if (!groups[key]) groups[key] = [];
                groups[key].push(t);
            });

            Object.entries(groups).forEach(([key, list]) => {
                const firstTest = list[0];
                const srv = typeof key === 'number' || !isNaN(key) ? services.find(s => s.id == key) : null;
                const isGroupHeader = srv && srv.parameters && srv.parameters.length > 0;
                
                if (isGroupHeader) {
                    printHtml += `
                        <tr style="background-color:#f8fafc; font-weight:bold;">
                            <td colspan="5" style="padding: 10px 8px; border-bottom:1.5px solid #e2e8f0; color:#1e3a8a;">${srv.name.toUpperCase()}</td>
                        </tr>
                    `;
                }

                list.forEach(t => {
                    const val = t.result_value !== null ? t.result_value : '-';
                    const isFlagged = t.status === 'flagged';
                    const flagLabel = isFlagged ? '<span class="flag-out">Fuori Range</span>' : '<span class="flag-normal">Normale</span>';
                    const indentStyle = isGroupHeader ? 'padding-left:25px;' : '';
                    
                    printHtml += `
                        <tr>
                            <td style="${indentStyle}">${t.test_name}</td>
                            <td style="text-align: center; font-weight:bold;">${val}</td>
                            <td>${t.unit || ''}</td>
                            <td>${t.reference_range || ''}</td>
                            <td style="text-align: center;">${flagLabel}</td>
                        </tr>
                    `;
                });
            });
        }

        printHtml += `
                    </tbody>
                </table>

                <div class="section-title">NOTE ED OSSERVAZIONI</div>
                <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; border-radius: 4px; padding: 12px; font-size: 0.85rem; min-height: 50px; white-space: pre-line;">
                    ${repNotes}
                </div>

                <div class="report-footer">
                    <div>Referto firmato digitalmente da Dr. LIS Administrator (NextCare)</div>
                    <div>Pagina 1 di 1</div>
                </div>
            </div>
        `;
    });

    printHtml += `
        </body>
        </html>
    `;

    const printWindow = window.open('', '_blank');
    if (!printWindow) {
        alert("Abilita i pop-up per procedere alla stampa.");
        return;
    }
    printWindow.document.write(printHtml);
    printWindow.document.close();
};
