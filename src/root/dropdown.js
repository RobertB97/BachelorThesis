$('.dropdown-menu a').click(function(){
    $('#selected').text($(this).text());
});

function ausgewählteStrategieSpeichern(){
    var daten = $("#addsimhead").val().split(",")
    var id = daten[0]
    $("#id_strategie").val(id);
}

function ausgewählteIsinSpeichern(){
    var daten = $("#addsimhead2").val().split(",")
    var isin = daten[0]
    console.log(isin)
    $("#id_ISIN").val(isin);
}
function alleEingabenSpeichern(){
    ausgewählteStrategieSpeichern()
    ausgewählteIsinSpeichern()
}