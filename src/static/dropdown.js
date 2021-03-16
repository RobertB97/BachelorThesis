$('.dropdown-menu a').click(function(){
    $('#selected').text($(this).text());
});

// Die ID der ausgewählten Strategie wird entnommen und in das versteckte Strategie Feld als Wert eingetragen
function ausgewählteStrategieSpeichern(){
    var daten = $("#addsimhead").val().split(",")
    var id = daten[0]
    $("#id_strategie").val(id);
}

// Die ISIN des ausgewählten Wertpapiers wird entnommen und in das versteckte ISIN Feld als Wert eingetragen
function ausgewählteIsinSpeichern(){
    var daten = $("#addsimhead2").val().split(",")
    var isin = daten[0]
    $("#id_isin").val(isin);
}
// Ruft alle Speicher-Funktionen auf
function alleEingabenSpeichern(){
    ausgewählteStrategieSpeichern()
    ausgewählteIsinSpeichern()
}