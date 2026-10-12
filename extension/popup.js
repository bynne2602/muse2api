/* Đọc Cookie muse.ai bằng API của trình duyệt và gửi đến máy chủ Muse2API đã chọn. */

const $ = (id) => document.getElementById(id);
const STORE = 'muse2api_ext_cfg';
const ESSENTIAL = ['hatch_sess', 'hatch_gw', 'hatch_vml', 'hatch_native_auth_device'];

function log(message, cls) {
  const el = $('log');
  el.className = 'show';
  el.textContent = message;
  if (cls) el.classList.add(cls);
}

function normBase(value) {
  let s = (value || '').trim();
  if (!s) return '';
  if (!/^https?:\/\//i.test(s)) s = 'https://' + s;
  return s.replace(/\/+$/, '').replace(/\/v1$/i, '');
}

async function loadCfg() {
  const saved = await chrome.storage.local.get(STORE);
  const cfg = saved[STORE] || {};
  if (cfg.base) $('base').value = cfg.base;
  if (cfg.key) $('key').value = cfg.key;
  if (cfg.label) $('label').value = cfg.label;

  // Khi mở popup ngay trên trang quản trị, lấy địa chỉ và API key từ URL.
  try {
    const [tab] = await chrome.tabs.query({active: true, currentWindow: true});
    const url = tab?.url ? new URL(tab.url) : null;
    if (url && /\/admin\/?$/.test(url.pathname)) {
      if (!cfg.base) $('base').value = url.origin;
      const key = new URLSearchParams(url.search).get('key');
      if (key) $('key').value = key;
    }
  } catch (_) { /* Người dùng có thể điền thủ công. */ }
}

async function saveCfg() {
  await chrome.storage.local.set({[STORE]: {
    base: normBase($('base').value),
    key: $('key').value.trim(),
    label: $('label').value.trim(),
  }});
}

async function grabCookies() {
  const all = await chrome.cookies.getAll({domain: 'muse.ai'});
  const cookies = {}, expires = {};
  for (const cookie of all) {
    const domain = (cookie.domain || '').replace(/^\./, '');
    if (!domain.endsWith('muse.ai')) continue;
    cookies[cookie.name] = cookie.value;
    if (cookie.expirationDate) expires[cookie.name] = Math.floor(cookie.expirationDate);
  }
  return {cookies, expires};
}

async function run() {
  const base = normBase($('base').value);
  const key = $('key').value.trim();
  const label = $('label').value.trim();
  $('log').className = '';

  if (!base) return log('Chưa có địa chỉ dịch vụ. Hãy mở trang quản trị Muse2API hoặc nhập địa chỉ.', 'bad');
  if (!key) return log('Chưa có API key. Hãy mở trang quản trị Muse2API hoặc nhập key.', 'bad');

  $('go').disabled = true;
  log('Đang đọc Cookie của muse.ai…');
  try {
    const {cookies, expires} = await grabCookies();
    const names = Object.keys(cookies);
    if (!names.length) {
      return log('Không tìm thấy Cookie muse.ai. Hãy đăng nhập muse.ai trong trình duyệt này rồi thử lại.', 'bad');
    }
    const missing = ESSENTIAL.filter((name) => !(name in cookies));
    if (missing.length) {
      return log(`Đã đọc ${names.length} Cookie nhưng còn thiếu: ${missing.join(', ')}. Hãy đăng nhập muse.ai đầy đủ rồi thử lại.`, 'warn');
    }

    log(`Đã đọc ${names.length} Cookie. Đang thêm tài khoản…`);
    const response = await fetch(base + '/admin/accounts', {
      method: 'POST',
      headers: {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + key},
      body: JSON.stringify({label, cookies, expires}),
    });
    const text = await response.text();
    let data;
    try { data = JSON.parse(text); } catch (_) { data = {raw: text}; }

    if (response.status === 401) {
      return log('API key không đúng (máy chủ trả về 401). Hãy kiểm tra lại key trên trang quản trị.', 'bad');
    }
    if (!response.ok) {
      return log(`Không thêm được tài khoản (HTTP ${response.status})\n${text.slice(0, 300)}`, 'bad');
    }

    const account = (data.added && data.added[0]) || {};
    await saveCfg();
    log(`✓ Đã thêm tài khoản\nTên: ${account.label || label || '(tự đặt)'}\nID: ${account.id || '?'}\nSố Cookie: ${account.cookie_count || names.length}\nPhiên hết hạn: ${account.expires_at ? new Date(account.expires_at * 1000).toLocaleString('vi-VN') : 'chưa rõ'}${data.warning ? `\n\nLưu ý: ${data.warning}` : ''}`, 'ok');
  } catch (error) {
    log(`Có lỗi: ${error?.message || String(error)}\n\nKiểm tra địa chỉ dịch vụ, trạng thái máy chủ và quyền kết nối của trình duyệt.`, 'bad');
  } finally {
    $('go').disabled = false;
  }
}

$('go').addEventListener('click', run);
loadCfg();
