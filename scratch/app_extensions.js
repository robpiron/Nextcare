// =============================================================
// NEXTCARE EXTENSIONS: DIRECT SSN ACCEPTANCE & CUSTOM HANDLERS
// =============================================================

// Temp recipe state tracker
window.tempSsnRecipe = {
    lis: null,
    ris: null
};

// Toggle RIS requester fields
window.toggleRisRequester = function(value) {
    const internalContainer = document.getElementById('ris-requester-internal-container');
    const externalContainer = document.getElementById('ris-requester-external-container');
    const internalSelect = document.getElementById('ris-requester-internal');
    const externalInput = document.getElementById('ris-requester-external');
    
    if (value === 'external') {
        if (internalContainer) internalContainer.style.display = 'none';
        if (externalContainer) externalContainer.style.display = 'block';
        if (internalSelect) internalSelect.removeAttribute('required');
        if (externalInput) externalInput.setAttribute('required', 'true');
    } else {
        if (internalContainer) internalContainer.style.display = 'block';
        if (externalContainer) externalContainer.style.display = 'none';
        if (internalSelect) internalSelect.setAttribute('required', 'true');
        if (externalInput) externalInput.removeAttribute('required');
    }
};

// Open recipe details modal
window.openSsnRecipeDetails = function(context) {
    window.ssnRecipeContext = context;
    const data = window.tempSsnRecipe[context] || {};
    
    document.getElementById('recipe-nre').value = data.nre || "";
    document.getElementById('recipe-exemption').value = data.exemption_code || "";
    document.getElementById('recipe-diagnosis').value = data.diagnostic_question || "";
    document.getElementById('recipe-date').value = data.recipe_date || new Date().toISOString().split('T')[0];
    document.getElementById('recipe-doctor').value = data.prescribing_doctor || "";
    document.getElementById('recipe-priority').value = data.priority_code || "P";
    document.getElementById('recipe-city').value = data.city || "";
    document.getElementById('recipe-asl-code').value = data.asl_code || "";
    document.getElementById('recipe-fse-obscure').value = data.fse_obscure_code || "";
    document.getElementById('recipe-fse-oppose').checked = data.fse_opposed ? true : false;
    
    openModal('modal-ssn-recipe-details');
};

// Save recipe details from modal
window.saveTempSsnRecipe = function() {
    const context = window.ssnRecipeContext || 'lis';
    const nre = document.getElementById('recipe-nre').value.trim();
    const exemption = document.getElementById('recipe-exemption').value.trim().toUpperCase();
    const diagnosis = document.getElementById('recipe-diagnosis').value.trim();
    const recDate = document.getElementById('recipe-date').value;
    const prescDoctor = document.getElementById('recipe-doctor').value.trim();
    const priority = document.getElementById('recipe-priority').value;
    const city = document.getElementById('recipe-city').value.trim();
    const aslCode = document.getElementById('recipe-asl-code').value || '101';
    const obscure = document.getElementById('recipe-fse-obscure').value || null;
    const opposed = document.getElementById('recipe-fse-oppose').checked;
    
    if (!nre || !recDate) {
        alert("Codice NRE e Data Ricetta sono obbligatori!");
        return;
    }
    
    window.tempSsnRecipe[context] = {
        nre,
        exemption_code: exemption,
        diagnostic_question: diagnosis,
        recipe_date: recDate,
        prescribing_doctor: prescDoctor,
        priority_code: priority,
        city,
        asl_code: aslCode,
        fse_obscure_code: obscure,
        fse_opposed: opposed
    };
    
    // Update summary card html
    const summaryHtml = `
        <div style="padding: 10px; background: rgba(249,115,22,0.08); border: 1px solid #f97316; border-radius: 6px; margin-top: 8px;">
            <div style="font-weight: bold; color: #c2410c; margin-bottom: 4px;">Ricetta SSN Collegata:</div>
            <div style="font-size: 0.85rem; color: var(--text-secondary); line-height: 1.4;">
                <strong>NRE:</strong> ${nre}<br>
                <strong>Esenzione:</strong> ${exemption || 'Nessuna'}<br>
                <strong>Priorità:</strong> ${priority} | <strong>ASL:</strong> ${aslCode}
            </div>
            <button type="button" class="btn btn-secondary btn-sm" onclick="window.openSsnRecipeDetails('${context}')" style="margin-top: 6px; padding: 2px 8px; font-size: 0.75rem;">Modifica Ricetta</button>
        </div>
    `;
    
    if (context === 'lis') {
        const sumEl = document.getElementById('sam-ssn-summary');
        if (sumEl) sumEl.innerHTML = summaryHtml;
        window.updateSampleCalculations();
    } else {
        const sumEl = document.getElementById('ris-ssn-summary');
        if (sumEl) sumEl.innerHTML = summaryHtml;
    }
    
    closeModal('modal-ssn-recipe-details');
};

// Handle recipe city ASL resolution
window.handleRecipeCityChange = async function() {
    const cityInput = document.getElementById('recipe-city');
    const aslInput = document.getElementById('recipe-asl-code');
    if (!cityInput || !aslInput) return;
    
    const cityVal = cityInput.value.trim().toLowerCase();
    if (!cityVal) {
        aslInput.value = '';
        return;
    }
    
    apiCall('/api/db-get-all', { table: 'ssn_asl_mapping' }, (res) => {
        if (res && res.success && res.data) {
            const match = res.data.find(a => a.city.toLowerCase() === cityVal);
            if (match) {
                aslInput.value = match.code || '101';
            } else {
                aslInput.value = '101'; // Default Fallback
            }
        } else {
            aslInput.value = '101';
        }
    });
};

// Toggle SSN checkboxes in LIS modal
window.toggleLisSsn = function(checked) {
    const sum = document.getElementById('sam-ssn-summary');
    const listino = document.getElementById('sam-listino');
    if (checked) {
        if (sum) sum.style.display = 'block';
        if (listino) {
            listino.value = 4; // Listino SSN
            listino.dispatchEvent(new Event('change'));
        }
        if (!window.tempSsnRecipe.lis) {
            window.openSsnRecipeDetails('lis');
        }
    } else {
        if (sum) {
            sum.innerHTML = '';
            sum.style.display = 'none';
        }
        if (listino) {
            listino.value = 1; // Privato Standard
            listino.dispatchEvent(new Event('change'));
        }
        window.tempSsnRecipe.lis = null;
    }
};

// Toggle SSN checkboxes in RIS modal
window.toggleRisSsn = function(checked) {
    const sum = document.getElementById('ris-ssn-summary');
    const listino = document.getElementById('ris-listino');
    if (checked) {
        if (sum) sum.style.display = 'block';
        if (listino) {
            listino.value = 4; // Listino SSN
            listino.dispatchEvent(new Event('change'));
        }
        if (!window.tempSsnRecipe.ris) {
            window.openSsnRecipeDetails('ris');
        }
    } else {
        if (sum) {
            sum.innerHTML = '';
            sum.style.display = 'none';
        }
        if (listino) {
            listino.value = 1; // Privato Standard
            listino.dispatchEvent(new Event('change'));
        }
        window.tempSsnRecipe.ris = null;
    }
};

// Handle company price list association
window.handleSampleCompanyChange = function() {
    const companyId = parseInt(document.getElementById('sam-company').value);
    const listinoSelect = document.getElementById('sam-listino');
    if (!listinoSelect) return;
    
    if (companyId) {
        const companies = DB.get('companies') || [];
        const co = companies.find(c => c.id === companyId);
        if (co) {
            listinoSelect.value = co.price_list_id;
        }
    } else {
        listinoSelect.value = 1;
    }
    renderSelectedLisTags();
};

window.handleRisCompanyChange = function() {
    const companyId = parseInt(document.getElementById('ris-company').value);
    const listinoSelect = document.getElementById('ris-listino');
    if (!listinoSelect) return;
    
    if (companyId) {
        const companies = DB.get('companies') || [];
        const co = companies.find(c => c.id === companyId);
        if (co) {
            listinoSelect.value = co.price_list_id;
        }
    } else {
        listinoSelect.value = 1;
    }
    
    const search = document.getElementById('ris-service-search');
    if (search && search.value) {
        search.dispatchEvent(new Event('input'));
    }
};

// RIS exam search autocomplete and info box
window.initRisSearchTags = function() {
    const searchInput = document.getElementById('ris-service-search');
    const hiddenInput = document.getElementById('ris-service');
    const suggestionsDiv = document.getElementById('ris-service-suggestions');
    const doseInfoDiv = document.getElementById('ris-service-dose-info');
    
    if (!searchInput || !suggestionsDiv) return;
    
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.toLowerCase().trim();
        if (!query) {
            suggestionsDiv.innerHTML = '';
            suggestionsDiv.style.display = 'none';
            return;
        }
        
        const listinoId = parseInt(document.getElementById('ris-listino')?.value || 1);
        const services = DB.get('medical_services') || [];
        const plItems = DB.get('price_list_items') || [];
        
        const risServices = services.filter(s => s.type === 'ris' || s.type === 'pacchetto');
        const matches = risServices.filter(s => s.name.toLowerCase().includes(query) || (s.code && s.code.toLowerCase().includes(query)));
        
        suggestionsDiv.innerHTML = '';
        if (matches.length === 0) {
            suggestionsDiv.innerHTML = '<div class="suggestion-item text-muted" style="padding: 8px; cursor: default;">Nessuna prestazione corrispondente</div>';
        } else {
            matches.slice(0, 15).forEach(m => {
                const item = plItems.find(p => p.price_list_id === listinoId && p.service_id === m.id);
                const price = Number(item ? item.price : (m.price || 0)) || 0;
                
                const div = document.createElement('div');
                div.className = 'suggestion-item';
                div.style.padding = '8px 12px';
                div.style.cursor = 'pointer';
                div.style.borderBottom = '1px solid rgba(0,0,0,0.05)';
                div.style.display = 'flex';
                div.style.justifyContent = 'space-between';
                div.style.alignItems = 'center';
                
                div.innerHTML = `
                    <span>${m.code ? `<strong>[${m.code}]</strong> ` : ''}${m.name}</span>
                    <span style="font-weight: bold; color: var(--primary);">€ ${price.toFixed(2)}</span>
                `;
                
                div.addEventListener('click', () => {
                    searchInput.value = `${m.code ? `[${m.code}] ` : ''}${m.name}`;
                    hiddenInput.value = m.id;
                    suggestionsDiv.style.display = 'none';
                    
                    const doseClasses = DB.get('dose_classes') || [];
                    if (m.dose_class_id) {
                        const dc = doseClasses.find(c => c.id === m.dose_class_id);
                        if (dc && doseInfoDiv) {
                            doseInfoDiv.style.display = 'block';
                            doseInfoDiv.innerHTML = `
                                <div style="margin-top: 8px; padding: 10px; background-color: var(--accent-light); border-left: 4px solid var(--accent-color); border-radius: 4px; font-size: 0.8rem; color: var(--text-main); line-height: 1.4;">
                                    <strong style="color: var(--accent-color);">D.Lgs. 101/2020: Classe di Dose ${dc.code}</strong> (${dc.range_msv})<br>
                                    <span style="font-size: 0.75rem; color: var(--text-secondary);">${dc.description}</span>
                                </div>
                            `;
                        } else if (doseInfoDiv) {
                            doseInfoDiv.style.display = 'none';
                            doseInfoDiv.innerHTML = '';
                        }
                    } else if (doseInfoDiv) {
                        doseInfoDiv.style.display = 'none';
                        doseInfoDiv.innerHTML = '';
                    }
                });
                suggestionsDiv.appendChild(div);
            });
        }
        suggestionsDiv.style.display = 'block';
    });
    
    document.addEventListener('click', (e) => {
        if (e.target !== searchInput && e.target !== suggestionsDiv) {
            suggestionsDiv.style.display = 'none';
        }
    });
};

// Print patient consents from prompt
window.printLisConsentFromPrompt = function() {
    const sampleId = parseInt(document.getElementById('print-prompt-sample-id').value);
    if (!sampleId) return;
    
    const samples = DB.get('lab_samples') || [];
    const sample = samples.find(s => s.id === sampleId);
    if (!sample) return;
    
    const labTests = DB.get('lab_tests') || [];
    const tests = labTests.filter(t => t.sample_id === sampleId);
    const serviceIds = tests.map(t => t.service_id);
    
    const requiredTemplates = window.evaluateRequiredConsents(sample.patient_id, serviceIds, null);
    if (requiredTemplates.length === 0) {
        alert("Nessun consenso informato obbligatorio per le prestazioni incluse in questo campione.");
        return;
    }
    
    requiredTemplates.forEach(tpl => {
        window.printPatientConsent(tpl.id, sample.patient_id, serviceIds, null);
    });
};

// Overwrite updateSampleCalculations to be SSN aware
const originalUpdateSampleCalculations = window.updateSampleCalculations;
window.updateSampleCalculations = function() {
    const ssnEnabled = document.getElementById('sam-ssn-enabled')?.checked;
    if (!ssnEnabled) {
        const insRow = document.getElementById('sam-calc-insurance-row');
        if (insRow) {
            const labelSpan = insRow.querySelector('span:first-child');
            const valSpan = document.getElementById('sam-calc-insurance');
            if (labelSpan) labelSpan.innerText = "Quota Coperta da Assicurazione:";
            if (valSpan) valSpan.style.color = '';
        }
        if (originalUpdateSampleCalculations) originalUpdateSampleCalculations();
        const insRowCheck = document.getElementById('sam-calc-insurance-row');
        if (insRowCheck && !document.getElementById('sam-claim')?.value) {
            insRowCheck.style.display = 'none';
        }
        return;
    }
    
    const inputs = document.querySelectorAll('#sam-selected-tests .sam-price-input');
    let rawSubtotal = 0;
    inputs.forEach(inp => {
        rawSubtotal += parseFloat(inp.value) || 0;
    });
    
    const exemptionCode = (window.tempSsnRecipe?.lis?.exemption_code || '').trim().toUpperCase();
    const exemptions = DB.get('ssn_exemptions') || [];
    const ex = exemptions.find(e => e.code === exemptionCode && e.active == 1);
    
    let ticket = 0;
    let isTotalExempt = false;
    if (ex) {
        if (parseFloat(ex.pct) >= 100.00) {
            isTotalExempt = true;
        }
    }
    
    const totalServices = inputs.length;
    const recipeCount = Math.ceil(totalServices / 8) || 1;
    
    if (isTotalExempt) {
        ticket = 0;
    } else {
        let recipePrices = [];
        for (let r = 0; r < recipeCount; r++) {
            recipePrices.push(0);
        }
        inputs.forEach((inp, idx) => {
            const recipeIdx = Math.floor(idx / 8);
            recipePrices[recipeIdx] += parseFloat(inp.value) || 0;
        });
        recipePrices.forEach(price => {
            const capped = Math.min(price, 36.15);
            ticket += capped + 10.00;
        });
    }
    
    const subEl = document.getElementById('sam-calc-subtotal');
    if (subEl) subEl.innerText = `€ ${rawSubtotal.toFixed(2)}`;
    const discEl = document.getElementById('sam-calc-discount');
    if (discEl) discEl.innerText = `€ 0.00 (Tariffe SSN)`;
    
    const insRow = document.getElementById('sam-calc-insurance-row');
    if (insRow) {
        insRow.style.display = 'flex';
        const labelSpan = insRow.querySelector('span:first-child');
        const valSpan = document.getElementById('sam-calc-insurance');
        if (labelSpan) labelSpan.innerText = "Quota a carico SSN (Rimborso):";
        if (valSpan) {
            valSpan.innerText = `€ ${(rawSubtotal - ticket).toFixed(2)}`;
            valSpan.style.color = 'var(--success)';
        }
    }
    
    const totEl = document.getElementById('sam-calc-total');
    if (totEl) totEl.innerText = `€ ${ticket.toFixed(2)}`;
    
    const stampDutyRow = document.getElementById('sam-calc-stamp-duty-row');
    if (stampDutyRow) stampDutyRow.style.display = 'none';
};

// Custom submit handler LIS
window.customLisSubmit = async function(e) {
    e.preventDefault();
    const ssnEnabled = document.getElementById('sam-ssn-enabled')?.checked;
    
    const patientId = parseInt(document.getElementById('sam-patient').value);
    const listinoId = parseInt(document.getElementById('sam-listino').value || 1);
    const claimIdVal = document.getElementById('sam-claim').value;
    const discountVal = parseFloat(document.getElementById('sam-discount-val').value || 0);
    const discountType = document.getElementById('sam-discount-type').value;
    const requestingDoctorVal = (document.getElementById('sam-requester')?.value || '').trim();
    const companyIdVal = document.getElementById('sam-company')?.value;
    const companyId = companyIdVal ? parseInt(companyIdVal) : null;
    
    if (selectedLisServiceIds.length === 0) {
        alert("Selezionare almeno un esame da eseguire tramite la barra di ricerca!");
        return;
    }
    
    if (ssnEnabled) {
        const recipeData = window.tempSsnRecipe?.lis;
        if (!recipeData || !recipeData.nre || !recipeData.recipe_date) {
            alert("Compilare i dati dell'impegnativa SSN cliccando su 'Modifica Ricetta'!");
            return;
        }
    }
    
    const services = DB.get('medical_services') || [];
    const tubeTypes = DB.get('tube_types') || [];
    const sessionUid = 'LIS-SESS-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
    
    const explodedServiceIds = window.expandServices(selectedLisServiceIds);
    const executionServices = services.filter(s => explodedServiceIds.includes(s.id));
    
    const servicesByTube = {};
    executionServices.forEach(srv => {
        if (srv.type !== 'lis') return;
        const tube = srv.sample_type || "Sangue (Tappo Viola)";
        if (!servicesByTube[tube]) {
            servicesByTube[tube] = [];
        }
        servicesByTube[tube].push(srv);
    });
    
    let newSam = null;
    
    for (const [tubeType, srvs] of Object.entries(servicesByTube)) {
        const matchedTube = tubeTypes.find(t => t.name === tubeType);
        const tubeSuffix = matchedTube ? matchedTube.suffix : '000';
        const barcodeNum = window.getNextBarcode(tubeSuffix);
        
        const sample = {
            patient_id: patientId,
            barcode: barcodeNum,
            sample_type: tubeType,
            status: 'da prelevare',
            session_uid: sessionUid,
            collected_at: null,
            collected_by: null,
            report_notes: "",
            requesting_doctor: requestingDoctorVal || null
        };
        const created = DB.insert('lab_samples', sample);
        if (!newSam) {
            newSam = created;
        }
        
        srvs.forEach(srv => {
            if (srv.parameters && srv.parameters.length > 0) {
                srv.parameters.forEach(p => {
                    const test = {
                        sample_id: created.id,
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
                    sample_id: created.id,
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
        
        DB.logAudit(4, "SAMPLE_COLLECT", "lab_samples", created.id, { barcode: barcodeNum, tests_count: srvs.length, session_uid: sessionUid });
    }
    
    const nonLisServices = executionServices.filter(s => s.type === 'ris' || s.type === 'visita');
    let createdStudyId = null;
    if (nonLisServices.length > 0) {
        nonLisServices.forEach(srv => {
            let studyType = 'XRAY';
            if (srv.type === 'visita') studyType = 'VISIT';
            else if (srv.name.toLowerCase().includes('risonanza') || srv.name.toLowerCase().includes('mri')) studyType = 'MRI';
            else if (srv.name.toLowerCase().includes('tac') || srv.name.toLowerCase().includes('computerizzata')) studyType = 'CT';
            else if (srv.name.toLowerCase().includes('eco')) studyType = 'ULTRASOUND';
            
            const study = {
                patient_id: patientId,
                doctor_id: 2,
                service_id: srv.id,
                study_type: studyType,
                scheduled_at: new Date().toISOString().substring(0, 16),
                status: srv.type === 'visita' ? 'in_progress' : 'scheduled',
                dicom_series_uid: '1.2.840.113619.2.' + Math.floor(Math.random()*9000) + '.' + Math.floor(Math.random()*900),
                report_text: null,
                signed_by: null,
                signed_at: null,
                requesting_doctor: requestingDoctorVal || null
            };
            const newStudy = DB.insert('radiology_studies', study);
            if (!createdStudyId) createdStudyId = newStudy.id;
            DB.logAudit(6, "ACCEPT_MIXED_BOOKING", "radiology_studies", newStudy.id, { type: studyType });
        });
    }
    
    let subtotal = 0;
    const customRates = {};
    const inputs = document.querySelectorAll('#sam-selected-tests .sam-price-input');
    inputs.forEach(input => {
        const srvId = parseInt(input.dataset.serviceId);
        const price = parseFloat(input.value || 0) || 0;
        customRates[srvId] = price;
        subtotal += price;
    });
    
    let createdInvoiceId = null;
    
    if (ssnEnabled) {
        const recipeData = window.tempSsnRecipe.lis;
        const totalServices = inputs.length;
        const recipeCount = Math.ceil(totalServices / 8) || 1;
        
        let ticket = 0;
        const exemptions = DB.get('ssn_exemptions') || [];
        const ex = exemptions.find(e => e.code === recipeData.exemption_code && e.active == 1);
        const isTotalExempt = ex && parseFloat(ex.pct) >= 100;
        
        for (let r = 0; r < recipeCount; r++) {
            const recipeNre = recipeCount > 1 ? `${recipeData.nre}-${r+1}` : recipeData.nre;
            const recipeRates = Object.entries(customRates).slice(r * 8, (r + 1) * 8);
            let recipeSubtotal = recipeRates.reduce((sum, [id, price]) => sum + price, 0);
            
            let recipeTicket = 0;
            if (isTotalExempt) {
                recipeTicket = 0;
            } else {
                recipeTicket = Math.min(recipeSubtotal, 36.15) + 10.00;
            }
            ticket += recipeTicket;
            
            const ssnRecipe = {
                nre: recipeNre,
                patient_id: patientId,
                exemption_code: recipeData.exemption_code || null,
                diagnostic_question: recipeData.diagnostic_question || null,
                recipe_date: recipeData.recipe_date,
                prescribing_doctor: recipeData.prescribing_doctor || null,
                priority_code: recipeData.priority_code,
                asl_code: recipeData.asl_code,
                ticket_amount: recipeTicket,
                refund_amount: recipeSubtotal - recipeTicket
            };
            DB.insert('ssn_recipes', ssnRecipe);
        }
        
        const invoiceNum = window.getNextInvoiceNumber();
        const invoice = {
            admission_id: null,
            appointment_id: null,
            sample_id: newSam ? newSam.id : null,
            study_id: newSam ? null : (createdStudyId || null),
            invoice_number: invoiceNum,
            issue_date: new Date().toISOString().split('T')[0],
            subtotal: subtotal,
            discount_value: 0,
            discount_type: 'flat',
            discount_amount: 0,
            price_list_id: 4, // SSN
            claim_id: null,
            insurance_covered_amount: subtotal - ticket,
            stamp_duty: 0,
            amount_due: ticket,
            amount_paid: 0.0,
            payment_status: 'unpaid',
            payment_method: 'Contanti',
            paid_at: null,
            patient_id: patientId,
            custom_rates: customRates,
            company_id: companyId
        };
        const inserted = DB.insert('invoices', invoice);
        createdInvoiceId = inserted.id;
        DB.logAudit(6, "AUTO_BILL_EMITTED", "invoices", null, { invoice_number: invoiceNum, amount: ticket, context: 'LIS_SSN_direct' });
        
        if (!recipeData.fse_opposed) {
            const fseTrans = {
                document_type: 'lis',
                document_id: newSam ? newSam.id : 1,
                status: 'pending',
                error_message: null,
                cda_xml: null
            };
            DB.insert('fse_transmissions', fseTrans);
        }
        
    } else {
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
        
        if (subtotal > 0) {
            let billingMode = 'single';
            if (claimIdVal) {
                const claim = DB.get('patient_claims').find(c => c.id === parseInt(claimIdVal));
                if (claim) {
                    const ins = DB.get('insurances').find(i => i.id === claim.insurance_id);
                    if (ins) {
                        billingMode = ins.billing_mode || 'single';
                    }
                }
            }
            
            if (billingMode === 'split' && insuranceCovered > 0) {
                const invNumPat = window.getNextInvoiceNumber();
                let stampDuty = 0.00;
                let amountDue = patientTotal;
                if (patientTotal > 77.47) {
                    stampDuty = 2.00;
                    amountDue = patientTotal + 2.00;
                }
                const invPat = {
                    admission_id: null,
                    appointment_id: null,
                    sample_id: newSam ? newSam.id : null,
                    study_id: newSam ? null : (createdStudyId || null),
                    invoice_number: invNumPat,
                    issue_date: new Date().toISOString().split('T')[0],
                    subtotal: patientTotal,
                    discount_value: 0,
                    discount_type: 'flat',
                    discount_amount: 0,
                    price_list_id: listinoId,
                    claim_id: parseInt(claimIdVal),
                    insurance_covered_amount: 0,
                    stamp_duty: stampDuty,
                    amount_due: amountDue,
                    amount_paid: 0.0,
                    payment_status: 'unpaid',
                    payment_method: null,
                    paid_at: null,
                    is_insurance_invoice: false,
                    custom_rates: customRates,
                    company_id: companyId
                };
                const insertedPat = DB.insert('invoices', invPat);
                createdInvoiceId = insertedPat.id;
                DB.logAudit(6, "AUTO_BILL_EMITTED", "invoices", null, { invoice_number: invNumPat, amount: amountDue, type: 'patient_split' });
                
                const invNumIns = window.getNextInvoiceNumber();
                const invIns = {
                    admission_id: null,
                    appointment_id: null,
                    sample_id: newSam ? newSam.id : null,
                    study_id: newSam ? null : (createdStudyId || null),
                    invoice_number: invNumIns,
                    issue_date: new Date().toISOString().split('T')[0],
                    subtotal: insuranceCovered,
                    discount_value: 0,
                    discount_type: 'flat',
                    discount_amount: 0,
                    price_list_id: listinoId,
                    claim_id: parseInt(claimIdVal),
                    insurance_covered_amount: 0,
                    stamp_duty: 0.00,
                    amount_due: insuranceCovered,
                    amount_paid: 0.0,
                    payment_status: 'unpaid',
                    payment_method: null,
                    paid_at: null,
                    is_insurance_invoice: true,
                    custom_rates: customRates,
                    company_id: companyId
                };
                DB.insert('invoices', invIns);
                DB.logAudit(6, "AUTO_BILL_EMITTED", "invoices", null, { invoice_number: invNumIns, amount: insuranceCovered, type: 'insurance_split' });
            } else {
                const invoiceNum = window.getNextInvoiceNumber();
                let stampDuty = 0.00;
                let amountDue = patientTotal;
                if (patientTotal > 77.47) {
                    stampDuty = 2.00;
                    amountDue = patientTotal + 2.00;
                }
                
                let isCompanyPost = false;
                if (companyId) {
                    const companies = DB.get('companies') || [];
                    const co = companies.find(c => c.id === companyId);
                    if (co && co.billing_type === 'company_post') {
                        isCompanyPost = true;
                    }
                }
                
                const invoice = {
                    admission_id: null,
                    appointment_id: null,
                    sample_id: newSam ? newSam.id : null,
                    study_id: newSam ? null : (createdStudyId || null),
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
                    amount_due: isCompanyPost ? 0 : amountDue,
                    amount_paid: 0.0,
                    payment_status: 'unpaid',
                    payment_method: null,
                    paid_at: null,
                    is_insurance_invoice: false,
                    custom_rates: customRates,
                    company_id: companyId,
                    is_company_post: isCompanyPost ? 1 : 0
                };
                const insertedInv = DB.insert('invoices', invoice);
                createdInvoiceId = insertedInv.id;
                DB.logAudit(6, "AUTO_BILL_EMITTED", "invoices", null, { invoice_number: invoiceNum, amount: amountDue });
            }
        }
    }
    
    closeModal('modal-add-sample');
    document.getElementById('form-add-sample').reset();
    selectedLisServiceIds = [];
    renderSamples();
    renderAdmissionsAndInvoices();
    window.populateRequesterDatalist();
    
    window.tempSsnRecipe.lis = null;
    const samSsnSummary = document.getElementById('sam-ssn-summary');
    if (samSsnSummary) samSsnSummary.style.display = 'none';
    
    if (newSam) {
        document.getElementById('print-prompt-sample-id').value = newSam.id;
        document.getElementById('print-prompt-barcode-label').innerText = newSam.barcode;
        openModal('modal-lis-print-prompt');
    }
    
    if (createdInvoiceId) {
        setTimeout(() => {
            window.promptDirectPaymentAndPrint(createdInvoiceId);
        }, 150);
    }
};

// Custom submit handler RIS
window.customRisSubmit = async function(e) {
    e.preventDefault();
    const ssnEnabled = document.getElementById('ris-ssn-enabled')?.checked;
    
    const srvId = parseInt(document.getElementById('ris-service').value);
    if (!srvId) {
        alert("Selezionare una prestazione RIS!");
        return;
    }
    
    if (ssnEnabled) {
        const recipeData = window.tempSsnRecipe?.ris;
        if (!recipeData || !recipeData.nre || !recipeData.recipe_date) {
            alert("Compilare i dati dell'impegnativa SSN cliccando su 'Modifica Ricetta'!");
            return;
        }
    }
    
    const services = DB.get('medical_services') || [];
    const srv = services.find(s => s.id === srvId);
    if (!srv) return;
    
    let studyType = 'XRAY';
    if (srv.name.toLowerCase().includes('risonanza') || srv.name.toLowerCase().includes('mri')) studyType = 'MRI';
    else if (srv.name.toLowerCase().includes('tac') || srv.name.toLowerCase().includes('computerizzata')) studyType = 'CT';
    else if (srv.name.toLowerCase().includes('eco')) studyType = 'ULTRASOUND';
    
    // External vs Internal doctor
    const reqType = document.getElementById('ris-requester-type').value;
    let doctorId = null;
    let requestingDoctorName = null;
    
    if (reqType === 'internal') {
        doctorId = parseInt(document.getElementById('ris-requester-internal').value) || null;
    } else {
        requestingDoctorName = document.getElementById('ris-requester-external').value.trim() || null;
    }
    
    const datetime = document.getElementById('ris-date').value;
    
    const companyIdVal = document.getElementById('ris-company')?.value;
    const companyId = companyIdVal ? parseInt(companyIdVal) : null;
    const listinoId = parseInt(document.getElementById('ris-listino')?.value || 1);
    
    const tsrmIdVal = document.getElementById('ris-tsrm')?.value;
    const tsrmId = tsrmIdVal ? parseInt(tsrmIdVal) : null;
    const repDocIdVal = document.getElementById('ris-reporting-doctor')?.value;
    const repDocId = repDocIdVal ? parseInt(repDocIdVal) : null;
    
    // Check reporting doctor agenda operational rules
    if (repDocId) {
        const agendas = DB.get('doctor_agendas') || [];
        const targetDateStr = datetime.split('T')[0];
        const targetDate = new Date(datetime);
        const docAgendas = agendas.filter(a => a.doctor_id === repDocId);
        const activeAgenda = docAgendas.find(a => targetDateStr >= a.start_date && targetDateStr <= a.end_date);
        
        let outsideAgenda = false;
        if (!activeAgenda) {
            outsideAgenda = true;
        } else {
            const weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
            const activeDaysList = activeAgenda.active_days.split(',');
            if (!activeDaysList.includes(weekdays[targetDate.getDay()])) {
                outsideAgenda = true;
            }
        }
        
        if (outsideAgenda) {
            const proceedOutside = await window.showCustomConfirm("Il medico refertante selezionato non ha un'agenda operativa valida o orari lavorativi abilitati per questa data. Vuoi comunque procedere ed effettuare l'accettazione fuori agenda?");
            if (!proceedOutside) return;
        }
    }
    
    // Overbooking checks on reporting doctor
    if (repDocId) {
        const hasAppConflict = (DB.get('appointments') || []).some(app => 
            app.doctor_id === repDocId && 
            window.compareDatetimes(app.appointment_datetime, datetime) && 
            app.status === 'scheduled'
        );
        const hasStudyConflict = (DB.get('radiology_studies') || []).some(st => 
            st.doctor_id === repDocId && 
            window.compareDatetimes(st.scheduled_at, datetime) && 
            st.status === 'scheduled'
        );
        
        if (hasAppConflict || hasStudyConflict) {
            const proceedOverbooking = await window.showCustomConfirm("ALLERTA OVERBOOKING! Lo slot orario selezionato per questo medico refertante è già occupato da un'altra prenotazione o accettazione. Vuoi forzare l'accettazione in overbooking?");
            if (!proceedOverbooking) return;
        }
    }
    
    const patientId = parseInt(document.getElementById('ris-patient').value);
    
    const study = {
        patient_id: patientId,
        doctor_id: doctorId,
        service_id: srvId,
        study_type: studyType,
        scheduled_at: datetime,
        status: 'scheduled',
        dicom_series_uid: '1.2.840.113619.2.' + Math.floor(Math.random()*9000) + '.' + Math.floor(Math.random()*900),
        report_text: null,
        signed_by: repDocId,
        signed_at: null,
        requesting_doctor: requestingDoctorName,
        tsrm_operator_id: tsrmId
    };
    
    const newStudy = DB.insert('radiology_studies', study);
    DB.logAudit(6, "RIS_REQUEST", "radiology_studies", newStudy.id, { type: study.study_type });
    
    const plItems = DB.get('price_list_items') || [];
    const item = plItems.find(p => p.price_list_id === listinoId && p.service_id === srvId);
    const price = Number(item ? item.price : (srv.price || 0)) || 0;
    
    let createdInvoiceId = null;
    
    if (ssnEnabled) {
        const recipeData = window.tempSsnRecipe.ris;
        
        let ticket = 0;
        const exemptions = DB.get('ssn_exemptions') || [];
        const ex = exemptions.find(e => e.code === recipeData.exemption_code && e.active == 1);
        const isTotalExempt = ex && parseFloat(ex.pct) >= 100;
        
        if (isTotalExempt) {
            ticket = 0;
        } else {
            ticket = Math.min(price, 36.15) + 10.00;
        }
        
        const ssnRecipe = {
            nre: recipeData.nre,
            patient_id: patientId,
            exemption_code: recipeData.exemption_code || null,
            diagnostic_question: recipeData.diagnostic_question || null,
            recipe_date: recipeData.recipe_date,
            prescribing_doctor: recipeData.prescribing_doctor || null,
            priority_code: recipeData.priority_code,
            asl_code: recipeData.asl_code,
            ticket_amount: ticket,
            refund_amount: price - ticket
        };
        DB.insert('ssn_recipes', ssnRecipe);
        
        const invoiceNum = window.getNextInvoiceNumber();
        const invoice = {
            admission_id: null,
            appointment_id: null,
            sample_id: null,
            study_id: newStudy.id,
            invoice_number: invoiceNum,
            issue_date: new Date().toISOString().split('T')[0],
            subtotal: price,
            discount_value: 0,
            discount_type: 'flat',
            discount_amount: 0,
            price_list_id: 4, // SSN
            claim_id: null,
            insurance_covered_amount: price - ticket,
            stamp_duty: 0,
            amount_due: ticket,
            amount_paid: 0.0,
            payment_status: 'unpaid',
            payment_method: 'Contanti',
            paid_at: null,
            patient_id: patientId,
            custom_rates: { [srvId]: price },
            company_id: companyId
        };
        const inserted = DB.insert('invoices', invoice);
        createdInvoiceId = inserted.id;
        DB.logAudit(6, "AUTO_BILL_EMITTED", "invoices", null, { invoice_number: invoiceNum, amount: ticket, context: 'RIS_SSN_direct' });
        
        if (!recipeData.fse_opposed) {
            const fseTrans = {
                document_type: 'visit',
                document_id: newStudy.id,
                status: 'pending',
                error_message: null,
                cda_xml: null
            };
            DB.insert('fse_transmissions', fseTrans);
        }
        
    } else {
        if (price > 0) {
            const invoiceNum = window.getNextInvoiceNumber();
            let stampDuty = 0.00;
            let amountDue = price;
            if (price > 77.47) {
                stampDuty = 2.00;
                amountDue = price + 2.00;
            }
            
            let isCompanyPost = false;
            if (companyId) {
                const companies = DB.get('companies') || [];
                const co = companies.find(c => c.id === companyId);
                if (co && co.billing_type === 'company_post') {
                    isCompanyPost = true;
                }
            }
            
            const invoice = {
                admission_id: null,
                appointment_id: null,
                sample_id: null,
                study_id: newStudy.id,
                invoice_number: invoiceNum,
                issue_date: new Date().toISOString().split('T')[0],
                subtotal: price,
                discount_value: 0,
                discount_type: 'flat',
                discount_amount: 0,
                price_list_id: listinoId,
                claim_id: null,
                insurance_covered_amount: 0,
                stamp_duty: stampDuty,
                amount_due: isCompanyPost ? 0 : amountDue,
                amount_paid: 0.0,
                payment_status: 'unpaid',
                payment_method: null,
                paid_at: null,
                is_insurance_invoice: false,
                custom_rates: { [srvId]: price },
                company_id: companyId,
                is_company_post: isCompanyPost ? 1 : 0
            };
            const inserted = DB.insert('invoices', invoice);
            createdInvoiceId = inserted.id;
            DB.logAudit(6, "AUTO_BILL_EMITTED", "invoices", null, { invoice_number: invoiceNum, amount: amountDue, context: 'RIS_manual_study' });
        }
    }
    
    closeModal('modal-add-ris');
    document.getElementById('form-add-ris').reset();
    window.renderRisStudies();
    window.renderAdmissionsAndInvoices();
    window.populateRequesterDatalist();
    
    window.tempSsnRecipe.ris = null;
    const risSsnSummary = document.getElementById('ris-ssn-summary');
    if (risSsnSummary) risSsnSummary.style.display = 'none';
    
    if (createdInvoiceId) {
        setTimeout(() => {
            window.promptDirectPaymentAndPrint(createdInvoiceId);
        }, 150);
    }
};

// Custom check-in submit to run clinical records generation in both SSN and Private paths
window.customCheckinSubmit = async function(e) {
    e.preventDefault();
    const appId = parseInt(document.getElementById('checkin-app-id').value);
    const ssnEnabled = document.getElementById('checkin-ssn-enabled').checked;
    
    const appointments = DB.get('appointments') || [];
    const app = appointments.find(a => a.id === appId);
    if (!app) return;
    
    const loggedUser = JSON.parse(localStorage.getItem('nextcare_logged_in_user') || '{}');
    const staffId = loggedUser.id || 1;
    
    const listinoId = ssnEnabled ? 4 : parseInt(document.getElementById('checkin-listino').value || 1);
    const claimId = ssnEnabled ? null : (document.getElementById('checkin-claim').value ? parseInt(document.getElementById('checkin-claim').value) : null);
    const discVal = ssnEnabled ? 0 : (parseFloat(document.getElementById('checkin-discount-val').value) || 0);
    const discType = ssnEnabled ? 'flat' : document.getElementById('checkin-discount-type').value;
    const payMethod = document.getElementById('checkin-payment-method').value;
    const tsrmId = document.getElementById('checkin-tsrm')?.value ? parseInt(document.getElementById('checkin-tsrm').value) : null;
    const repDocId = document.getElementById('checkin-reporting-doctor')?.value ? parseInt(document.getElementById('checkin-reporting-doctor').value) : null;
    const reqDoc = document.getElementById('checkin-requester')?.value.trim() || '';
    const obscure = document.getElementById('checkin-fse-obscure')?.value || null;
    const opposed = ssnEnabled ? document.getElementById('checkin-fse-oppose').checked : false;
    
    const appServices = DB.get('appointment_services') || [];
    const services = DB.get('medical_services') || [];
    const srvIds = appServices.filter(as => as.appointment_id === appId).map(as => as.service_id);
    const booked = services.filter(sv => srvIds.includes(sv.id));
    
    const lisServices = booked.filter(s => s.type === 'lis');
    const risServices = booked.filter(s => s.type === 'ris');
    
    const customRates = {};
    const inputs = document.querySelectorAll('#checkin-services-list .checkin-price-input');
    inputs.forEach(inp => {
        const srvId = parseInt(inp.dataset.serviceId);
        const price = parseFloat(inp.value) || 0;
        customRates[srvId] = price;
    });
    
    const srvSubtotal = parseFloat(document.getElementById('checkin-calc-subtotal').innerText.replace(/[^0-9.-]/g, '')) || 0;
    
    let createdInvoiceId = null;
    let totalTicket = 0;
    
    if (ssnEnabled) {
        const nre = document.getElementById('checkin-ssn-nre').value.trim();
        const exemption = document.getElementById('checkin-ssn-exemption').value.trim();
        const diagnosis = document.getElementById('checkin-ssn-diagnosis').value.trim();
        const recDate = document.getElementById('checkin-ssn-date').value;
        const prescDoctor = document.getElementById('checkin-ssn-doctor').value.trim();
        const priority = document.getElementById('checkin-ssn-priority').value;
        const aslCode = document.getElementById('checkin-ssn-asl-code').value || '101';
        
        if (!nre || !recDate) {
            alert("Codice NRE e Data Ricetta sono campi obbligatori per l'accettazione SSN!");
            return;
        }
        
        const totalServices = inputs.length;
        const recipeCount = Math.ceil(totalServices / 8) || 1;
        
        const exemptions = DB.get('ssn_exemptions') || [];
        const ex = exemptions.find(e => e.code === exemption && e.active == 1);
        const isTotalExempt = ex && parseFloat(ex.pct) >= 100;
        
        for (let r = 0; r < recipeCount; r++) {
            const recipeNre = recipeCount > 1 ? `${nre}-${r+1}` : nre;
            const recipeRates = Object.entries(customRates).slice(r * 8, (r + 1) * 8);
            let recipeSubtotal = recipeRates.reduce((sum, [id, price]) => sum + price, 0);
            
            let recipeTicket = 0;
            if (isTotalExempt) {
                recipeTicket = 0;
            } else {
                recipeTicket = Math.min(recipeSubtotal, 36.15) + 10.00;
            }
            totalTicket += recipeTicket;
            
            const ssnRecipe = {
                nre: recipeNre,
                patient_id: app.patient_id,
                exemption_code: exemption || null,
                diagnostic_question: diagnosis || null,
                recipe_date: recDate,
                prescribing_doctor: prescDoctor || null,
                priority_code: priority,
                asl_code: aslCode,
                ticket_amount: recipeTicket,
                refund_amount: recipeSubtotal - recipeTicket
            };
            DB.insert('ssn_recipes', ssnRecipe);
        }
        
        DB.update('appointments', appId, { 
            status: 'in_progress', 
            fse_obscure_code: obscure 
        });
        
        const invoiceNum = window.getNextInvoiceNumber();
        const invoice = {
            admission_id: null,
            appointment_id: appId,
            sample_id: null,
            study_id: null,
            invoice_number: invoiceNum,
            issue_date: new Date().toISOString().split('T')[0],
            subtotal: srvSubtotal,
            discount_value: 0,
            discount_type: 'flat',
            discount_amount: 0,
            price_list_id: 4,
            claim_id: null,
            insurance_covered_amount: srvSubtotal - totalTicket,
            stamp_duty: 0,
            amount_due: totalTicket,
            amount_paid: 0.0,
            payment_status: 'unpaid',
            payment_method: payMethod,
            paid_at: null,
            patient_id: app.patient_id,
            custom_rates: customRates
        };
        const inserted = DB.insert('invoices', invoice);
        createdInvoiceId = inserted.id;
        DB.logAudit(staffId, "CHECKIN_SSN_APPOINTMENT", "appointments", appId, { 
            ssn_enabled: true, 
            fse_obscure_code: obscure,
            recipes_count: recipeCount
        });
        
        if (!opposed) {
            const fseTrans = {
                document_type: app.doctor_id ? 'visit' : 'lis',
                document_id: appId,
                status: 'pending',
                error_message: null,
                cda_xml: null
            };
            DB.insert('fse_transmissions', fseTrans);
        }
        
    } else {
        const updateFields = { status: 'in_progress', fse_obscure_code: obscure };
        if (tsrmId) updateFields.tsrm_operator_id = tsrmId;
        DB.update('appointments', appId, updateFields);
        
        const sub = parseFloat(document.getElementById('checkin-calc-subtotal').innerText.replace(/[^0-9.-]/g, '')) || 0;
        const disc = parseFloat(document.getElementById('checkin-calc-discount').innerText.replace(/[^0-9.-]/g, '')) || 0;
        const insCovered = parseFloat(document.getElementById('checkin-calc-insurance').innerText.replace(/[^0-9.-]/g, '')) || 0;
        const stamp = parseFloat(document.getElementById('checkin-calc-stamp-duty').innerText.replace(/[^0-9.-]/g, '')) || 0;
        const due = parseFloat(document.getElementById('checkin-calc-total').innerText.replace(/[^0-9.-]/g, '')) || 0;
        
        const invoiceNum = window.getNextInvoiceNumber();
        const invoice = {
            admission_id: null,
            appointment_id: appId,
            sample_id: null,
            study_id: null,
            invoice_number: invoiceNum,
            issue_date: new Date().toISOString().split('T')[0],
            subtotal: sub,
            discount_value: discVal,
            discount_type: discType,
            discount_amount: disc,
            price_list_id: listinoId,
            claim_id: claimId,
            insurance_covered_amount: insCovered,
            stamp_duty: stamp,
            amount_due: due,
            amount_paid: 0.0,
            payment_status: 'unpaid',
            payment_method: payMethod,
            paid_at: null,
            patient_id: app.patient_id,
            custom_rates: customRates
        };
        const inserted = DB.insert('invoices', invoice);
        createdInvoiceId = inserted.id;
        DB.logAudit(staffId, "CHECKIN_APPOINTMENT", "appointments", appId, { ssn_enabled: false, fse_obscure_code: obscure });
        
        const fseTrans = {
            document_type: app.doctor_id ? 'visit' : 'lis',
            document_id: appId,
            status: 'pending',
            error_message: null,
            cda_xml: null
        };
        DB.insert('fse_transmissions', fseTrans);
    }
    
    let createdSample = null;
    if (lisServices.length > 0) {
        const sessionUid = 'LIS-SESS-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
        const tubeTypes = DB.get('tube_types') || [];
        const servicesByTube = {};
        lisServices.forEach(srv => {
            const tube = srv.sample_type || "Sangue (Tappo Viola)";
            if (!servicesByTube[tube]) servicesByTube[tube] = [];
            servicesByTube[tube].push(srv);
        });
        
        for (const [tubeType, srvs] of Object.entries(servicesByTube)) {
            const matchedTube = tubeTypes.find(t => t.name === tubeType);
            const tubeSuffix = matchedTube ? matchedTube.suffix : '000';
            const barcodeNum = window.getNextBarcode(tubeSuffix);
            
            const sample = {
                patient_id: app.patient_id,
                barcode: barcodeNum,
                sample_type: tubeType,
                status: 'da prelevare',
                session_uid: sessionUid,
                collected_at: null,
                collected_by: null,
                report_notes: "",
                requesting_doctor: reqDoc || null
            };
            const created = DB.insert('lab_samples', sample);
            if (!createdSample) createdSample = created;
            
            srvs.forEach(srv => {
                if (srv.parameters && srv.parameters.length > 0) {
                    srv.parameters.forEach(p => {
                        const test = {
                            sample_id: created.id,
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
                        sample_id: created.id,
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
        }
        DB.update('appointments', appId, { session_uid: sessionUid });
    }
    
    const createdStudyIds = [];
    if (risServices.length > 0) {
        risServices.forEach(s => {
            const newStudy = {
                patient_id: app.patient_id,
                service_id: s.id,
                study_type: s.study_type || 'XRAY',
                scheduled_at: app.appointment_datetime,
                status: 'scheduled',
                dicom_series_uid: `1.3.6.1.4.1.25403.345050719076124.847.${appId}`,
                report_text: null,
                signed_by: repDocId,
                signed_at: null,
                fse_obscure_code: obscure,
                requesting_doctor: reqDoc || null,
                tsrm_operator_id: tsrmId,
                doctor_id: app.doctor_id || null
            };
            const created = DB.insert('radiology_studies', newStudy);
            createdStudyIds.push(created.id);
        });
    }
    
    await DB.waitForSync();
    closeModal('modal-checkin-appointment');
    
    alert(`Accettazione completata con successo!\n\n- Prenotazione completata.\n\n${createdSample ? `- Campione LIS creato con Barcode: ${createdSample.barcode}\n\n` : ''}${createdStudyIds.length > 0 ? `- Generati ${createdStudyIds.length} studi/visite in elaborazione.\n\n` : ''}- Emessa fattura di € ${srvSubtotal.toFixed(2)} (Quota ticket/dovuta: € ${(ssnEnabled ? totalTicket : srvSubtotal).toFixed(2)}).`);
    
    if (typeof window.loadActiveTab === 'function') window.loadActiveTab();
    
    if (createdInvoiceId) {
        setTimeout(() => {
            window.promptDirectPaymentAndPrint(createdInvoiceId);
        }, 150);
    }
};

// Redefine Allowed tabs configurations including license
window.getAllowedTabsConfig = function() {
    const defaultAllowedTabs = {
        admin: ['dashboard', 'core', 'cup', 'admission', 'accounting', 'lis', 'ris', 'unified-reports', 'services', 'clinics', 'hris', 'reporting-services', 'reporting-acceptances', 'notifications', 'templates', 'insurance-config', 'integrations', 'database', 'lis-logs', 'faq', 'bi-dashboard', 'warehouse', 'rehab', 'portals', 'fse-transmissions', 'doctor-compensations', 'ssn-billing', 'sts-transmission', 'audit-logs', 'license'],
        tsrm: ['ris', 'faq'],
        segreteria: ['dashboard', 'core', 'cup', 'admission', 'accounting', 'unified-reports', 'reporting-services', 'reporting-acceptances', 'notifications', 'faq'],
        doctor_1: ['dashboard', 'unified-reports', 'ris', 'reporting-services', 'reporting-acceptances', 'faq'],
        doctor_2: ['dashboard', 'unified-reports', 'ris', 'reporting-services', 'reporting-acceptances', 'faq'],
        infermiere: ['lis'],
        biologo: ['dashboard', 'lis', 'unified-reports', 'clinics', 'notifications', 'faq']
    };
    try {
        const custom = localStorage.getItem('nextcare_role_permissions');
        if (custom) {
            const parsed = JSON.parse(custom);
            if (parsed.admin) {
                if (!parsed.admin.includes('database')) parsed.admin.push('database');
                if (!parsed.admin.includes('audit-logs')) parsed.admin.push('audit-logs');
                if (!parsed.admin.includes('license')) parsed.admin.push('license');
            }
            return parsed;
        }
    } catch(e) {
        console.error("Error reading role permissions", e);
    }
    return defaultAllowedTabs;
};

// Redefine loadRolePermissions using iOS toggle switches
window.loadRolePermissions = function(role) {
    const roleSelect = document.getElementById('perm-role-select');
    if (!roleSelect) return;
    const selectedRole = role || roleSelect.value;
    
    const allowedConfig = window.getAllowedTabsConfig();
    const allowedList = allowedConfig[selectedRole] || [];
    
    const allTabs = [
        { id: 'dashboard', label: 'Dashboard Principale' },
        { id: 'bi-dashboard', label: 'Statistiche Direzionali (BI)' },
        { id: 'core', label: 'Anagrafiche (Pazienti)' },
        { id: 'cup', label: 'Pianificazione CUP (Agenda)' },
        { id: 'admission', label: 'Accettazione & Ricovero' },
        { id: 'accounting', label: 'Fatturazione & Cassa' },
        { id: 'lis', label: 'Laboratorio Analisi (LIS)' },
        { id: 'ris', label: 'Radiologia & Refertazione (RIS)' },
        { id: 'warehouse', label: 'Gestione Magazzino' },
        { id: 'rehab', label: 'Fisioterapia & Riabilitazione' },
        { id: 'portals', label: 'Portale Pazienti & Aziende' },
        { id: 'fse-transmissions', label: 'Monitor Trasmissioni FSE' },
        { id: 'doctor-compensations', label: 'Gestione Compensi Medici' },
        { id: 'ssn-billing', label: 'Accettazione SSN & Rendicontazione' },
        { id: 'sts-transmission', label: 'Sistema Tessera Sanitaria (730)' },
        { id: 'unified-reports', label: 'Archivio Referti Unificati' },
        { id: 'services', label: 'Configurazione Prestazioni' },
        { id: 'clinics', label: 'Branca / Agende Medici' },
        { id: 'hris', label: 'Gestione Personale (HRIS)' },
        { id: 'reporting-services', label: 'Reportistica Prestazioni' },
        { id: 'reporting-acceptances', label: 'Reportistica Accettazioni' },
        { id: 'notifications', label: 'Configurazione Notifiche' },
        { id: 'templates', label: 'Modelli Referti & Consensi' },
        { id: 'insurance-config', label: 'Listini & Tariffe Convenzioni' },
        { id: 'lis-logs', label: 'Simulatori & Log Strumenti LIS' },
        { id: 'integrations', label: 'Integrazioni Middleware LIS' },
        { id: 'database', label: 'Configurazione Database & PACS' },
        { id: 'audit-logs', label: 'Log Attività (Audit)' },
        { id: 'license', label: 'Gestione Licenze & Attivazione' },
        { id: 'faq', label: 'FAQ & Supporto AI' }
    ];
    
    const grid = document.getElementById('permissions-grid');
    if (!grid) return;
    grid.innerHTML = '';
    
    allTabs.forEach(t => {
        const isChecked = allowedList.includes(t.id) ? 'checked' : '';
        const isDisabled = (selectedRole === 'admin' && (t.id === 'database' || t.id === 'audit-logs' || t.id === 'license')) ? 'disabled' : '';
        
        grid.innerHTML += `
            <div class="switch-container" style="display: flex; align-items: center; justify-content: space-between; padding: 6px 10px; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; font-size: 0.8rem; width: 100%; box-sizing: border-box;">
                <span style="color: var(--text-primary); font-weight: 500;">${t.label}</span>
                <label class="switch" style="margin-bottom: 0;">
                    <input type="checkbox" class="perm-checkbox" data-tab-id="${t.id}" ${isChecked} ${isDisabled}>
                    <span class="slider"></span>
                </label>
            </div>
        `;
    });
};

// Initial setup, datalists and form bindings
(function() {
    // Populate exemptions datalists once at load
    apiCall('/api/db-get-all', { table: 'ssn_exemptions' }, (res) => {
        const dl1 = document.getElementById('checkin-exemption-list');
        const dl2 = document.getElementById('recipe-exemption-list');
        if (res && res.success && res.data) {
            const html = res.data.map(ex => `<option value="${ex.code}">${ex.name} (Quota: ${ex.pct}%)</option>`).join('');
            if (dl1) dl1.innerHTML = html;
            if (dl2) dl2.innerHTML = html;
        }
    });

    // Event listener for check-in exemption changes
    const chkEx = document.getElementById('checkin-ssn-exemption');
    if (chkEx) {
        chkEx.addEventListener('input', () => window.updateCheckinCalculations());
        chkEx.addEventListener('change', () => window.updateCheckinCalculations());
    }

    // Intercept window.openModal to clear SSN states when opening add dialogs
    const originalOpenModal = window.openModal;
    window.openModal = function(modalId) {
        if (modalId === 'modal-add-sample') {
            const chk = document.getElementById('sam-ssn-enabled');
            if (chk) chk.checked = false;
            const sum = document.getElementById('sam-ssn-summary');
            if (sum) {
                sum.innerHTML = '';
                sum.style.display = 'none';
            }
            window.tempSsnRecipe.lis = null;
            const listino = document.getElementById('sam-listino');
            if (listino) listino.value = 1;
        } else if (modalId === 'modal-add-ris') {
            const chk = document.getElementById('ris-ssn-enabled');
            if (chk) chk.checked = false;
            const sum = document.getElementById('ris-ssn-summary');
            if (sum) {
                sum.innerHTML = '';
                sum.style.display = 'none';
            }
            window.tempSsnRecipe.ris = null;
            const listino = document.getElementById('ris-listino');
            if (listino) listino.value = 1;
            
            // Reset requester type
            const reqType = document.getElementById('ris-requester-type');
            if (reqType) {
                reqType.value = 'internal';
                window.toggleRisRequester('internal');
            }
            const reqExt = document.getElementById('ris-requester-external');
            if (reqExt) reqExt.value = '';
        }
        if (originalOpenModal) originalOpenModal(modalId);
    };

    // Clone and re-bind forms to run the correct handlers
    const checkinForm = document.getElementById('form-checkin-appointment');
    if (checkinForm) {
        const newForm = checkinForm.cloneNode(true);
        checkinForm.parentNode.replaceChild(newForm, checkinForm);
        newForm.addEventListener('submit', window.customCheckinSubmit);
    }

    const samForm = document.getElementById('form-add-sample');
    if (samForm) {
        const newForm = samForm.cloneNode(true);
        samForm.parentNode.replaceChild(newForm, samForm);
        newForm.addEventListener('submit', window.customLisSubmit);
    }

    const risForm = document.getElementById('form-add-ris');
    if (risForm) {
        const newForm = risForm.cloneNode(true);
        risForm.parentNode.replaceChild(newForm, risForm);
        newForm.addEventListener('submit', window.customRisSubmit);
    }

    // Bind change listeners to listinos for autocomplete/search tag pricing sync
    const samListino = document.getElementById('sam-listino');
    if (samListino) {
        samListino.addEventListener('change', () => {
            if (typeof renderSelectedLisTags === 'function') renderSelectedLisTags();
        });
    }

    const risListino = document.getElementById('ris-listino');
    if (risListino) {
        risListino.addEventListener('change', () => {
            const search = document.getElementById('ris-service-search');
            if (search && search.value) {
                search.dispatchEvent(new Event('input'));
            }
        });
    }

    // Initialize RIS service search autocomplete
    window.initRisSearchTags();
})();
