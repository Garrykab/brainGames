$(document).ready(() => {
    let functionGet = function(token, url, container) {
        $.ajax({
            type: "POST",
            url: url,
            data: {
                'csrfmiddlewaretoken': token,
            },
            success: function(result) {
                // console.log(result)
                container.empty().append(result);
            },
            async: false
        });
    };

    $(document).on('click', '#btn-valider', function(e) {
        e.preventDefault();

        var username = $('#username').val();
        var password = $('#password').val();

        if (username != "") {
            $('#username').removeClass('is-invalid');
            $('#error-username').text('')

            if(password != "") {
                $('#password').removeClass('is-invalid')
                $('#error-password').text('')
                
                return $('#formAuth').submit()
            }

            $('#password').addClass('is-invalid')
            $('#error-password').text('Veuillez remplir le champ mot de passe')
            return
        }

        $('#username').addClass('is-invalid');
        $('#error-username').text('Veuillez remplir le champ nom utilisateur')
        return
    });

    $(document).on('click', '#btn-Add-equipe', function(e) {
        e.preventDefault();

        var token = $(this).data('token');
        var name = $('#name-equipe').val();
        var promotion = $('#promotion-equipe').val();

        if (name != "") {
            $('#name-equipe').removeClass('is-invalid');
            $('#error-name-equipe').text('')

            if(functionCheck($('#name-equipe').attr('url-nameExiste'), name, token) != "exists") {
                $('#name-equipe').removeClass('is-invalid');
                $('#error-name-equipe').text('');

                if(promotion != "") {
                    $('#promotion-equipe').removeClass('is-invalid')
                    $('#error-promotion-equipe').text('')

                    if(functionCheck($('#promotion-equipe').attr('url-promotionExiste'), promotion, token) != "exists") {
                        $('#promotion-equipe').removeClass('is-invalid');
                        $('#error-promotion-equipe').text('');
                    
                        return $('#formAddEquipe').submit()
                    }

                    $('#promotion-equipe').addClass('is-invalid')
                    $('#error-promotion-equipe').text('Cette promotion a déjà une équipe.')
                    return
                }
    
                $('#promotion-equipe').addClass('is-invalid')
                $('#error-promotion-equipe').text('Ce champ est obligatoire')
                return
            }

            $('#name-equipe').addClass('is-invalid');
            $('#error-name-equipe').text('Ce nom d\'équipe existe déjà');
            return

        }

        $('#name-equipe').addClass('is-invalid');
        $('#error-name-equipe').text('Ce champ est obligatoire')
        return
    });

    function functionCheck(url, param, token) {
        var res = "";
    
        $.ajax({
            type: "POST",
            url: url,
            data: {
                'csrfmiddlewaretoken': token,
                'param': param
            },
            success: function(result) {
                console.log(result);
                res = result.exists ? "exists" : "not_exists";
            },
            error: function(xhr, status, error) {
                console.error("Error: " + error);
            },
            async: false
        });
    
        return res;
    }    

    $(document).on('click', '#list-question', function(e) {
        functionGet(
            $('meta[name="csrf-token"]').attr('content'),
            $(this).data('url'),
            $('#datas-question')
        )
    });

    $(document).on('click', '#btn-deleteQuestion', function(e) {
        e.preventDefault();

        var id_question = $(this).data('id');
        var token = $('meta[name="csrf-token"]').attr('content');
        var url = $(this).data('url');

        $.ajax({
            type: 'POST',
            url: url,
            data: {
                'csrfmiddlewaretoken' : token,
                id_question : id_question
            },
            success: function(response) {
                // console.log(response);

                if(response.success) {
                    $('#message').addClass('text-success').text(response.message);
                    $('#alert_info').addClass('alert-success').show();
                    // getAllEtudiants();

                    if(response.questions < 1) {
                        functionGet(
                            $('meta[name="csrf-token"]').attr('content'),
                            $('#list-question').data('url'),
                            $('#datas-question')
                        )
                    }

                    $('#content-' + id_question).addClass('animated slideOutLeft');

                    setTimeout(function() {
                        $('#content-' + id_question).remove();
                    }, 1500);
                    return
                }

                $('#message').addClass('text-danger').text(response.message);
                return $('#alert_info').addClass('alert-danger').show();
            },
            error: function(xhr, status, error) {
                console.error(xhr.responseText);
            }
        });

        return;
    });

    $('#btn-addCsv').prop('disabled', true);

    $(document).on('change', '#fichiercsv', function() {
        var monFichier = $('#fichiercsv')[0].files[0];
        var fileName = monFichier.name;
        var fileExtension = fileName.split('.').pop().toLowerCase();
        var validFileType = monFichier.type === 'text/csv' || monFichier.type === 'application/vnd.ms-excel';
        var validFileExtension = fileExtension === 'csv';
        
        if (!validFileType || !validFileExtension) {
            $('#btn-addCsv').prop('disabled', true);
            return $('#error-fichiercsv').text('Seuls les fichiers CSV sont pris en charge...');
        }
        
        $('#btn-addCsv').prop('disabled', false);
        return $('#error-fichiercsv').text('');
    });
    

    // $(document).on('click', '#ex3-tab-2', function(e) {
    //     $('#ex3-tabs-1').removeClass('animated slideInLeft')
    //     $('#ex3-tabs-2').addClass('animated slideInRight')
    //     console.log(2)

    // });

    $(document).on('click', '#btnSaveConfig', function(e) {
        e.preventDefault();

        var token = $('meta[name="csrf-token"]').attr('content');
        var url = $(this).data('url');
        nombre_qst = $('#nombre_question').val()
        duree = $('#duration').val()
        difficulte = $('#difficulte').val()

        if(nombre_qst != "" && nombre_qst > 0 && $.isNumeric(nombre_qst)) {
            nombre_qst = parseInt(nombre_qst)
            $('#nombre_question').removeClass('is-invalid')

            if(duree != "" && duree > 0 && $.isNumeric(duree)) {
                duree = parseInt(duree)
                $('#duration').removeClass('is-invalid')

                $.ajax({
                    type: 'POST',
                    url: url,
                    data: {
                        'csrfmiddlewaretoken' : token,
                        nombre_qst : nombre_qst,
                        duree : duree,
                        difficulte : difficulte
                    },
                    success: function(response) {
                        // console.log(response);
        
                        if(response.success) {
                            $('#message').removeClass('text-danger').addClass('text-success').text(response.message);
                            $('#alert_info').removeClass('alert-danger').addClass('alert-success').show();
                            return
                        }

                        $('#message').removeClass('text-success').addClass('text-danger').text(response.message);
                        return $('#alert_info').removeClass('alert-success').addClass('alert-danger').show();
                    },
                    error: function(xhr, status, error) {
                        console.error(xhr.responseText);
                    }
                });
        
                return;
            }
            return $('#duration').addClass('is-invalid')
        }
        return $('#nombre_question').addClass('is-invalid')
    });
})