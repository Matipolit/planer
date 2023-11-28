function setup() {
  addNewPerson();
}

// params - name, tasks
function addNewPerson() {
  var contentWrapper = document.createElement('div');
  contentWrapper.setAttribute('class', 'tasksContentWrapper');

  var content = document.createElement('div');
  content.setAttribute('class', 'tasksContent');

  var checkbox = document.createElement('input');
  checkbox.setAttribute('type', 'checkbox');

  var name = document.createElement('h3');
  name.textContent = 'IMIE NAZWISKO';

  var tasks = ["XD", "XD"];

  var taskList = document.createElement('ul');

  for (let task of tasks) {
    var item = document.createElement('li');
    item.innerText = task;
    taskList.appendChild(item);
  }

  content.appendChild(checkbox);
  content.appendChild(name);
  content.appendChild(taskList);

  contentWrapper.appendChild(content);

  document.getElementById('tasks').appendChild(contentWrapper);
}
