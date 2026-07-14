


    // Discourse forum  popup and the live support feature goes here
var discourse_msg_active=false;

         $(document).ready(function(){

             $('#Discourse_button').click(function(){

               if(discourse_msg_active==false){

                $('#Discourse_Forum').slideDown(300);
                 discourse_msg_active=true;

               }else{
                    $('#Discourse_Forum').slideUp(300);

                 discourse_msg_active=false;

               }

            });
            // Controls for the close button for this popup
            $('#Discourse_close').click(function(){
                $('#Discourse_Forum').slideUp(300);
                discourse_msg_active=false;

            });
  })
