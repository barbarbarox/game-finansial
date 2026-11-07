/**
 * characterCreate.js — Alur pembuatan karakter baru.
 * Memilih gender, memasukkan nama karakter, nama ayah, dan nama ibu.
 * Input validation: 1-20 karakter, huruf/spasi/apostrof/tanda hubung.
 * Anti-XSS: textContent only.
 */

export function createCharacterModal(container, onComplete) {
  const backdrop = document.createElement('div');
  backdrop.className = 'lj-modal-backdrop';

  const modal = document.createElement('div');
  modal.className = 'lj-panel charcreate-panel';
  modal.setAttribute('role', 'dialog');
  modal.setAttribute('aria-modal', 'true');

  const header = document.createElement('div');
  header.className = 'panel-header';
  const title = document.createElement('h2');
  title.className = 'panel-title';
  title.textContent = 'Buat Karakter Siswa SMA';
  header.appendChild(title);

  const form = document.createElement('form');
  form.className = 'charcreate-form';

  // Gender Selection
  const genderGroup = document.createElement('div');
  genderGroup.className = 'form-group';
  const genderLabel = document.createElement('label');
  genderLabel.textContent = 'Pilih Karakter:';
  const genderSelect = document.createElement('select');
  genderSelect.className = 'input-field';

  const optM = document.createElement('option');
  optM.value = 'm';
  optM.textContent = 'Laki-laki (Siswa SMA)';
  const optF = document.createElement('option');
  optF.value = 'f';
  optF.textContent = 'Perempuan (Siswi SMA)';

  genderSelect.appendChild(optM);
  genderSelect.appendChild(optF);
  genderGroup.appendChild(genderLabel);
  genderGroup.appendChild(genderSelect);

  // Name Fields
  function makeInput(labelText, placeholder, defaultValue) {
    const group = document.createElement('div');
    group.className = 'form-group';
    const label = document.createElement('label');
    label.textContent = labelText;
    const input = document.createElement('input');
    input.type = 'text';
    input.maxLength = 20;
    input.required = true;
    input.placeholder = placeholder;
    input.value = defaultValue;
    input.className = 'input-field';
    group.appendChild(label);
    group.appendChild(input);
    return { group, input };
  }

  const charName = makeInput('Nama Karakter:', 'Contoh: Budi', 'Budi');
  const fatherName = makeInput('Nama Ayah:', 'Contoh: Pak Joko', 'Pak Joko');
  const motherName = makeInput('Nama Ibu:', 'Contoh: Bu Siti', 'Bu Siti');

  // Submit button
  const submitBtn = document.createElement('button');
  submitBtn.type = 'submit';
  submitBtn.className = 'btn btn-primary';
  submitBtn.textContent = 'Mulai Petualangan';

  form.appendChild(genderGroup);
  form.appendChild(charName.group);
  form.appendChild(fatherName.group);
  form.appendChild(motherName.group);
  form.appendChild(submitBtn);

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const nameRegex = /^[a-zA-Z\s'-]{1,20}$/;

    const name = charName.input.value.trim();
    const father = fatherName.input.value.trim();
    const mother = motherName.input.value.trim();

    if (!nameRegex.test(name) || !nameRegex.test(father) || !nameRegex.test(mother)) {
      alert('Nama hanya boleh terdiri dari huruf, spasi, tanda hubung, atau apostrof (1-20 karakter).');
      return;
    }

    backdrop.remove();
    onComplete({
      gender: genderSelect.value,
      name,
      fatherName: father,
      motherName: mother
    });
  });

  modal.appendChild(header);
  modal.appendChild(form);
  backdrop.appendChild(modal);
  container.appendChild(backdrop);
}

