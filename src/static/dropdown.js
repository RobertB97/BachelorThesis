$('.dropdown-menu a').click(function(){
    $('#selected').text($(this).text());
});

function ausgewählteStrategieSpeichern(){
    var daten = $("#gewählteStrategie").val().split(",")
    var strategieJSON = {
        "id": daten[0],
        "name":daten[1],

    }    
    $("#id_strategie").val(JSON.stringify(strategieJSON));

}