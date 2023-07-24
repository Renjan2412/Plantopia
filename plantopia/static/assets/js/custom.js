$(document).on('submit', '#check-address-form', function(e) {
    e.preventDefault();
    console.log('check address submission ')
    var formData = new FormData(this);
    

    $.ajax({
        method:"POST",
        url:'/my-address/',
        data:formData,
        processData:false,
        contentType:false,
        success:function(response){
            $('#newAddressModal').modal('hide');
            swal({
                title:"Success",
                text:"Address Updated!",
                icon:"success",
                timer:4000,
                button:false,

            }).then(function(){
                $('#address-block').load(location.href + ' #address-block', function(){
                    $(document).on('click', '#newAdd', function() {
                        $('#newAddressModal').modal('show');
                    });
                });
            });
            
        }
    })

});