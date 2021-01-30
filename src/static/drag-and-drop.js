const draggableListe = document.querySelectorAll('.draggable') // Liste mit allen verschiebbaren Elementen
const containerListe = document.querySelectorAll('.container') // Liste mit allen Containern

/** 
 * fügt zu jeden draggable element die eventlistener dragstart und dragend hinzu
 * wenn das element verschoben wird, wird die class dragging hinzugefügt, 
 * wenn element losgelassen wird, wird die class dragging wieder entfernt   * 
 */
draggableListe.forEach(draggable => {
  draggable.addEventListener('dragstart', () => {
    draggable.classList.add('dragging')
    draggable.querySelector('.Reihenfolgennummer').innerHTML = ""
  }) 
  draggable.addEventListener('dragend', () => {

    draggable.classList.remove('dragging')
    
  }) 
})

/**
 * fügt jedem container den eventlistener für das event "dragover" hinzu, dieses event ereignet sich, wenn ein element über einem container ist
 * es wird dann überprüft, ob das verschobene Element ein folgendes Element hat,
  * wenn nein, dann wird das verschobene Element einfach angehängt
  * wenn ja, dann wird es vor das folgende Element eingesetzt
*/
containerListe.forEach(container => {
  container.addEventListener('dragover', e => { 
    e.preventDefault() // per default ist das verschieben nicht erlaubt und das mouse-icon wird verändert. Dieser Befehl verhindert dies
    const folgendesElement = naechstesElementNachDraggable(container, e.clientY)
    const draggable = document.querySelector('.dragging') //das element welches aktuell verschoben wird
    if (folgendesElement == null) {
      container.appendChild(draggable)      
    } else {
      container.insertBefore(draggable, folgendesElement)
    }
    elementeNummerieren()
  })
})

/**
 * @description
 * Es werden die Regeln, die sich im Container "Verwendete Regeln" befinden in ein JSON gespeichert und als String in das Form-Feld "regeln" eingefügt 
 * um die Nutzerauswahl speichern zu können 
 */
function ausgewählteRegelnSpeichern(){
  //go through all rules in the container and add only the necessary elements to a json
  var regeln = elementChildNodes(containerListe[0])
  regelnJson = []
  regeln.forEach(regel=>{
    var regelChildren = elementChildNodes(regel)
    regelJson = {
      "id": regelChildren[1].innerHTML,
      "name": regelChildren[2].innerHTML,
      "code": regelChildren[3].innerHTML,
    }
    regelnJson.push(regelJson)
  })
  
  $("#id_regeln").val(JSON.stringify(regelnJson));
}


/**
 * @description
 * Es werden alle Elemente von allen Containern von oben nach unten durchnummeriert
 */
function elementeNummerieren(){
  containerListe.forEach(container =>{
    children = elementChildNodes(container)
    counter = 1;
    children.forEach(element => {
      element.querySelector('.Reihenfolgennummer').innerHTML=counter;
      counter++;
    })
  })
}

/**
 * @param {*} element Das Element von welchem die Unterelemente  zurückgegeben werden sollen
 * @description
 * Gibt die Unterelemente für das ausgewählte Element zurück
 */
function elementChildNodes (element) {
  var childNodes = element.childNodes,
      unterelemente = [],
      i = childNodes.length;
  while (i--) {
      if (childNodes[i].nodeType == 1) {
        unterelemente.unshift(childNodes[i]);
      }
  }
  return unterelemente;
}
/**
 *  
 * @param {*} container Der Container, in welchen das Element verschoben wird
 * @param {*} y Die y-Position des Mauszeigers
 * @description Bestimmt das Element, welches sich unter dem Mauszeigers befindet (wenn dieses Element existiert) .
 */

function naechstesElementNachDraggable(container, y) { 
  const draggableElemente = [...container.querySelectorAll('.draggable:not(.dragging)')] // alle Elemente im Container außer das Element, welches verschoben wird
  return draggableElemente.reduce((closest, unterelement) => { //reduce ermittelt das Element, das sich nach dem Mauszeiger befindet, anhand der y-Position
    const box = unterelement.getBoundingClientRect()
    const abstandNext = y - box.top - box.height / 2 
    if (abstandNext < 0 && abstandNext > closest.abstandNext) { // abstandNext < 0 => über einem Element, abstandNext > 0 unter einem Element
      return { abstandNext: abstandNext, element: unterelement }
    } else {
      return closest
    }
  }, { abstandNext: Number.NEGATIVE_INFINITY }).element
}