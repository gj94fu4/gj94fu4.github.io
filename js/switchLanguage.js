function switchTo(current, next) {
  document.getElementById(current).style.display = 'none';
  document.getElementById(next).style.display = '';
}

function switchLanguage(lang) {
  document.getElementById('zh').style.display = lang === 'zh' ? '' : 'none';
  document.getElementById('en').style.display = lang === 'en' ? '' : 'none';
}