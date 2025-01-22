const button = document.getElementById('toggleButton');
const component1 = document.getElementById('response');
const component2 = document.getElementById('text');

button.addEventListener('click', () => {
  alert("sds")
  if (component1.classList.contains('hidden')) {
    component1.classList.remove('hidden');
    component2.classList.add('hidden');
  } else {
    component1.classList.add('hidden');
    component2.classList.remove('hidden');
  }
});