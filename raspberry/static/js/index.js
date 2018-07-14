$(document).ready(function(){

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
                'estilo': 'btn-danger',
                'acao': 'desligar'
            },
            false: {
                'status': 'desligada',
                'estilo': 'btn-success',
                'acao': 'ligar'
            }
        };
        var value = map[status.rele];
        $('#span-status').text(value.status);
        $('#btn-acao').removeClass('btn-danger btn-success').addClass(value.estilo);
        $('#btn-acao').text(value.acao);
    }

    atualizar();
    setInterval(atualizar, 3000);
});
