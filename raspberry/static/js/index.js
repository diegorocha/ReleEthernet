$(document).ready(function(){
    console.log("Teste");

    $('#btn-acao').click(function(){
        var actionUrl = "api/rele/toggle";
        $.ajax({
            url: actionUrl,
            type:"POST",
            success: aplicar,
            error: onError
        });
    });

    function atualizar(){
        var statusUrl = "api/rele";
        $.ajax({
            url: statusUrl,
            success: aplicar,
            error: onError
        });
    }

    function onError(qXHR, textStatus, errorThrown){

    }

    function aplicar(status){
        var map = {
            true: {
                'status': 'ligada',
                'acao': 'desligar'
            },
            false: {
                'status': 'desligada',
                'acao': 'ligar'
            }
        };
        $('#span-status').text(map[status.rele].status);
        $('#btn-acao').text(map[status.rele].acao);
    }

    atualizar();
    setInterval(atualizar, 5000);
});
