Qualtrics.SurveyEngine.addOnload(function() {
  const baseURL = 'https://acbc-api-20250620-170752-29e5f1e7fc59.herokuapp.com';
  const q = this;
  q.hideNextButton();

  // 1) Collect BYO selections from dropdowns or checkboxes
  function collectSelectedAttributes() {
    // Example: attributes defined as Qualtrics Embedded Data: attributeNames = ['brand','material','style']
    const attrNames = ['brand','material','style'];
    const selected = {};
    attrNames.forEach(name => {
      // assume each attribute rendered as checkboxes with class `.byo-${name}`
      const elems = q.getQuestionContainer().querySelectorAll(`.byo-${name}:checked`);
      selected[name] = Array.from(elems).map(el => el.value);
    });
    return selected;
  }

  // 2) Render screening concepts into a container
  function renderScreeningTasks(tasks) {
    const cont = q.getQuestionContainer().querySelector('#screening-container');
    cont.innerHTML = '';
    tasks.forEach(task => {
      const div = document.createElement('div');
      div.className = 'screening-task';
      div.innerHTML = `
        <p>Concept ${task.position}:</p>
        ${Object.entries(task.concept).map(([k,v]) => `<strong>${k}:</strong> ${v}`).join('<br>')}
        <br>
        <label><input type="radio" name="resp-${task.id}" value="true"> Like</label>
        <label><input type="radio" name="resp-${task.id}" value="false"> Dislike</label>
        <hr>
      `;
      cont.appendChild(div);
    });
    // add submit button
    const btn = document.createElement('button');
    btn.textContent = 'Submit Screening';
    btn.onclick = submitScreeningResponses;
    cont.appendChild(btn);
  }

  // 3) Read screening responses and send to API
  function submitScreeningResponses() {
    const responses = Array.from(q.getQuestionContainer().querySelectorAll('.screening-task')).map(div => {
      const name = div.querySelector('input[type=radio]').name;
      return div.querySelector(`input[name='${name}']:checked`).value === 'true';
    });
    const sid = Qualtrics.SurveyEngine.getEmbeddedData('sessionId');
    fetch(`${baseURL}/api/screening/responses`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ session_id: sid, responses })
    })
    .then(() => loadTournament(1));
  }

  // 4) Render tournament choice set
  function renderChoiceTask(concepts, taskNumber) {
    const cont = q.getQuestionContainer().querySelector('#tournament-container');
    cont.innerHTML = `<p>Task ${taskNumber} - Choose one:</p>`;
    concepts.forEach(c => {
      const label = document.createElement('label');
      label.innerHTML = `
        <input type="radio" name="choice" value="${c.id}"> 
        ${Object.entries(c.attributes).map(([k,v])=>`${k}: ${v}`).join(', ')}
        <br>
      `;
      cont.appendChild(label);
    });
    const btn = document.createElement('button');
    btn.textContent = 'Submit Choice';
    btn.onclick = () => submitChoiceResponse(taskNumber);
    cont.appendChild(btn);
  }

  // 5) API calls
  async function sendBYO() {
    const attrs = collectSelectedAttributes();
    const sid = Qualtrics.SurveyEngine.getEmbeddedData('sessionId') || null;
    const res = await fetch(`${baseURL}/api/byo-config`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ session_id: sid, selected_attributes: attrs })
    });
    const data = await res.json();
    Qualtrics.SurveyEngine.setEmbeddedData('sessionId', data.session_id);
    loadScreening();
  }

  async function loadScreening() {
    const sid = Qualtrics.SurveyEngine.getEmbeddedData('sessionId');
    const res = await fetch(`${baseURL}/api/screening/design?session_id=${sid}`);
    const tasks = await res.json();
    renderScreeningTasks(tasks);
  }

  async function loadTournament(taskNumber) {
    const sid = Qualtrics.SurveyEngine.getEmbeddedData('sessionId');
    const res = await fetch(`${baseURL}/api/tournament/choice?session_id=${sid}&task_number=${taskNumber}`);
    const payload = await res.json();
    renderChoiceTask(payload.concepts, payload.task_number);
  }

  async function submitChoiceResponse(taskNumber) {
    const sid = Qualtrics.SurveyEngine.getEmbeddedData('sessionId');
    const choiceId = q.getQuestionContainer().querySelector('input[name="choice"]:checked').value;
    const res = await fetch(`${baseURL}/api/tournament/choice-response`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ session_id: sid, task_number: taskNumber, selected_concept_id: parseInt(choiceId) })
    });
    const data = await res.json();
    if (data.next_task) {
      loadTournament(data.next_task);
    } else {
      q.showNextButton();
    }
  }

  // 6) Initialize flow: bind BYO button, render containers
  q.getQuestionContainer().innerHTML = `
    <div id="byo-section">
      <!-- Render your BYO inputs (dropdowns/checkboxes) here -->
      <button id="byo-btn">Submit Configuration</button>
    </div>
    <div id="screening-container"></div>
    <div id="tournament-container"></div>
  `;
  q.getQuestionContainer().querySelector('#byo-btn').onclick = sendBYO;
});