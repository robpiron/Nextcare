import re

with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Find all function calls, e.g. functionName(...)
# Matches identifiers followed by '(' (ignoring spaces)
calls = re.findall(r'\b([a-zA-Z0-9_]+)\s*\(', code)
unique_calls = set(calls)

# Find all function definitions in app.js
# 1. function name(...)
defined_functions = set(re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', code))
# 2. name = function(...)
defined_functions.update(re.findall(r'\b([a-zA-Z0-9_]+)\s*=\s*function\s*\(', code))
# 3. window.name = function(...)
defined_functions.update(re.findall(r'window\.([a-zA-Z0-9_]+)\s*=\s*function\s*\(', code))
# 4. name = (...) =>
defined_functions.update(re.findall(r'\b([a-zA-Z0-9_]+)\s*=\s*\(.*?\)\s*=>', code))

# Known standard built-ins and library functions in NextCare project
built_ins = {
    'parseInt', 'parseFloat', 'alert', 'prompt', 'confirm', 'setTimeout', 'setInterval',
    'isNaN', 'String', 'Number', 'Boolean', 'Date', 'RegExp', 'Error', 'Array', 'Object',
    'fetch', 'clearInterval', 'clearTimeout', 'addEventListener', 'removeEventListener',
    'querySelector', 'querySelectorAll', 'getElementById', 'createElement', 'appendChild',
    'setAttribute', 'getAttribute', 'removeAttribute', 'classList', 'focus', 'click',
    'reset', 'submit', 'push', 'forEach', 'map', 'filter', 'find', 'some', 'every', 'reduce',
    'sort', 'slice', 'splice', 'split', 'join', 'includes', 'indexOf', 'lastIndexOf',
    'toLowerCase', 'toUpperCase', 'trim', 'replace', 'replaceAll', 'match', 'test',
    'substring', 'substr', 'toFixed', 'toString', 'preventDefault', 'stopPropagation',
    'log', 'warn', 'error', 'info', 'debug', 'dir', 'table', 'clear', 'write', 'readAsDataURL',
    'getContext', 'fillRect', 'fillRect', 'strokeRect', 'clearRect', 'beginPath', 'arc',
    'ellipse', 'moveTo', 'lineTo', 'stroke', 'fill', 'quadraticCurveTo', 'arcTo', 'rect',
    'createLinearGradient', 'createRadialGradient', 'addColorStop', 'drawImage', 'scale',
    'rotate', 'translate', 'save', 'restore', 'measureText', 'fillText', 'strokeText',
    'open', 'close', 'focus', 'print', 'showModal', 'setItem', 'getItem', 'removeItem',
    'stringify', 'parse', 'insert', 'update', 'get', 'set', 'logAudit', 'active', 'remove',
    'add', 'toggle', 'keys', 'values', 'entries', 'some', 'every', 'find', 'filter', 'map',
    'forEach', 'push', 'pop', 'shift', 'unshift', 'concat', 'slice', 'splice', 'indexOf',
    'includes', 'join', 'reverse', 'sort', 'split', 'match', 'search', 'replace', 'trim',
    'toLowerCase', 'toUpperCase', 'charAt', 'charCodeAt', 'substring', 'substr', 'toFixed',
    'toPrecision', 'toString', 'valueOf', 'now', 'parse', 'UTC', 'getFullYear', 'getMonth',
    'getDate', 'getDay', 'getHours', 'getMinutes', 'getSeconds', 'getMilliseconds', 'getTime',
    'getTimezoneOffset', 'setFullYear', 'setMonth', 'setDate', 'setHours', 'setMinutes',
    'setSeconds', 'setMilliseconds', 'setTime', 'toLocaleString', 'toLocaleDateString',
    'toLocaleTimeString', 'toUTCString', 'toISOString', 'toJSON', 'floor', 'ceil', 'round',
    'abs', 'max', 'min', 'random', 'pow', 'sqrt', 'sin', 'cos', 'tan', 'asin', 'acos',
    'atan', 'atan2', 'log', 'exp', 'PI', 'E', 'LN2', 'LN10', 'LOG2E', 'LOG10E', 'SQRT1_2',
    'SQRT2', 'FormData', 'FileReader', 'XMLHttpRequest', 'ActiveXObject', 'eval', 'exec',
    'testDbConnection', 'testSmtpConnection', 'sendSimulatedEmail', 'printActiveModalReport',
    'printDivContent', 'retrievePacsStudy', 'openLisReportView', 'openRisReportView',
    'openPatientDetail', 'openCheckinModal', 'openResultsModal', 'openAddAppointmentModal',
    'openEditAppointmentModal', 'openCancelAppointmentModal', 'validateSample',
    'openDicomViewer', 'sendDicomWorklist', 'runPacsQueryRetrieve', 'drawLisTrendChart',
    'switchSubTab', 'switchTab', 'switchConfigSubTab', 'loadActiveTab', 'renderDashboard',
    'renderPatients', 'renderServices', 'renderAppointments', 'renderSamples', 'renderRisStudies',
    'renderClinicsAndEquipment', 'renderAdmissionsAndInvoices', 'renderStaffAndShifts',
    'renderAccountingDashboard', 'renderReportingServices', 'renderReportingAcceptances',
    'renderSentEmails', 'loadTemplateSettings', 'loadSelectedEmailTemplate', 'initNavigation',
    'initTheme', 'initGlobalSearch', 'initFormHandlers', 'initDicomControls', 'initAiAssistant',
    'initRichEditors', 'initServiceToggles', 'initLisSearchTags', 'initCupSearchTags',
    'loadSqlSchema', 'populateDropdownsEquipmentSetup', 'initDbSettingsForm',
    'initTemplateSettingsForm', 'initServiceFilters', 'initAccountingFilters', 'initNewFeatures',
    'showDbStatus', 'changeUserRole', 'updatePatientClaimsDropdown', 'populatePriceListsDropdown',
    'populateTubeTypesDropdown', 'handleCheckinSubmit', 'handleAddClaimSubmit', 'handleEditInvoiceSubmit',
    'handleSmtpSettingsSubmit', 'handleAddInsuranceSubmit', 'handleAddTubeTypeSubmit',
    'filterServicesRealtime', 'populateBranchFilter', 'buildPatientTimeline', 'buildPatientAuditLogs',
    'generateAiAnswer', 'addAiMessage', 'toggleServiceFormFields', 'addSelectedLisTest',
    'addSelectedCupService', 'validateCupDoctorAgendaSelection', 'findAndRenderFreeSlots',
    'syncActiveSlotBadge', 'drawDicomImage', 'openAddInsuranceModal', 'deleteInsurance',
    'openAddTubeTypeModal', 'deleteTubeType', 'renderInsurancesTable', 'loadListinoPricesTable',
    'renderTubesTable', 'printReportingServices', 'exportReportingServicesCSV', 'printReportingAcceptances',
    'exportReportingAcceptancesCSV', 'openEditClinicModal', 'deleteClinic', 'openEditEquipmentModal',
    'deleteEquipment', 'openEditServiceModal', 'deleteService', 'updateEquipmentStatus'
}

undefined_calls = []
for c in unique_calls:
    if c not in defined_functions and c not in built_ins:
        # Check if it's called as a method (like obj.methodName() or Math.max())
        # We can look at the characters before it
        pattern = r'([a-zA-Z0-9_\$]+)\.' + re.escape(c) + r'\s*\('
        is_method = len(re.findall(pattern, code)) > 0
        if not is_method:
            undefined_calls.append(c)

print(f"Undefined function calls ({len(undefined_calls)}):")
for uc in undefined_calls:
    # Print context
    pattern = r'.*?\b' + re.escape(uc) + r'\s*\(.*'
    matches = re.findall(pattern, code)
    print(f"- '{uc}':")
    for m in matches[:3]:
        print(f"  JS: {m.strip()}")
