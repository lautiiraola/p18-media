/**
 * P18 · receptor del formulario "Sumate" en Google Sheets.
 * Se pega en Extensiones → Apps Script de la planilla y se implementa como aplicación web.
 * Pasos completos en LEEME.md (misma carpeta).
 */

var SHEET_NAME = 'Respuestas';
var SERIE_SHEET = 'Serie A mis 18';
// Opcional: un mail que recibe un aviso por cada respuesta nueva. Vacío = sin aviso.
var NOTIFY_EMAIL = '';

var PERFILES = ['joven', 'proyecto', 'speaker', 'organizacion'];
var TEMAS = [
  'arte-y-diseno', 'vinculos-y-comunicacion', 'finanzas-personales', 'habitos-y-disciplina',
  'como-vender', 'autoestima', 'perseverancia', 'redes', 'inteligencia-artificial', 'a-mis-18',
  // Creatividad (nuevo departamento)
  'pensamiento-creativo', 'musica-y-audiovisual', 'escritura-y-relatos'
];
var HEADERS = ['Fecha', 'Nombre', 'Email', 'Perfil', 'Temas', 'Otro tema', 'Origen'];

function doPost(e) {
  var data;
  try {
    data = JSON.parse(e.postData.contents);
  } catch (err) {
    return reply({ ok: false, error: 'formato' });
  }

  // Campo trampa: los humanos no lo ven, los bots suelen completarlo.
  if (data.sitio) return reply({ ok: true });

  if (data.tipo === 'serie') return guardarSerie(data);

  var nombre = clean(data.nombre, 120);
  var email = clean(data.email, 200);
  if (!nombre || !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) {
    return reply({ ok: false, error: 'datos' });
  }
  var perfil = PERFILES.indexOf(data.perfil) >= 0 ? data.perfil : 'joven';
  var temas = (Array.isArray(data.temas) ? data.temas : []).filter(function (t) { return TEMAS.indexOf(t) >= 0; });
  var otro = clean(data.otro, 600);
  var origen = clean(data.origen, 60);

  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    var sheet = getSheet();
    sheet.appendRow([new Date(), nombre, email, perfil, temas.join(', '), otro, origen].map(safeCell));
  } finally {
    lock.releaseLock();
  }

  if (NOTIFY_EMAIL) {
    MailApp.sendEmail(NOTIFY_EMAIL, 'P18 · Nueva respuesta de ' + nombre,
      'Nombre: ' + nombre + '\nEmail: ' + email + '\nPerfil: ' + perfil +
      '\nTemas: ' + (temas.join(', ') || '—') + '\nOtro tema: ' + (otro || '—'));
  }

  return reply({ ok: true });
}

// Avisos de la serie «A mis 18»: nombre, email y celular en su propia hoja.
function guardarSerie(data) {
  var nombre = clean(data.nombre, 120);
  var email = clean(data.email, 200);
  var telefono = clean(data.telefono, 40);
  var digitos = telefono.replace(/\D/g, '');
  if (!nombre || !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || digitos.length < 8 || digitos.length > 15) {
    return reply({ ok: false, error: 'datos' });
  }
  var lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    getSheet(SERIE_SHEET, ['Fecha', 'Nombre', 'Email', 'Celular', 'Origen'])
      .appendRow([new Date(), nombre, email, telefono, clean(data.origen, 60)].map(safeCell));
  } finally {
    lock.releaseLock();
  }
  if (NOTIFY_EMAIL) {
    MailApp.sendEmail(NOTIFY_EMAIL, 'P18 · Nuevo aviso para A mis 18: ' + nombre,
      'Nombre: ' + nombre + '\nEmail: ' + email + '\nCelular: ' + telefono);
  }
  return reply({ ok: true });
}

function getSheet(name, headers) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheetName = name || SHEET_NAME;
  var sheet = ss.getSheetByName(sheetName) || ss.insertSheet(sheetName);
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(headers || HEADERS);
    sheet.setFrozenRows(1);
  }
  return sheet;
}

function clean(value, max) {
  return String(value == null ? '' : value).trim().slice(0, max);
}

// Evita que un texto que empieza con =, +, - o @ se ejecute como fórmula en la planilla.
function safeCell(value) {
  return typeof value === 'string' && /^[=+\-@]/.test(value) ? "'" + value : value;
}

function reply(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
