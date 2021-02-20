$('.dropdown-menu a').click(function(){
    $('#selected').text($(this).text());
});

function ausgewählteStrategieSpeichern(){
    var daten = $("#addsimhead").val().split(",")
    var id = daten[0]
    $("#id_strategie").val(id);
}