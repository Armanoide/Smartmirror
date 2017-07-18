/**
 * Created by norbert on 8/07/2017.
 */


var MenuManager = function () {

    var instance = this;
    instance.isOpen = false;

    var button = document.getElementById('cn-button'),
        wrapper = document.getElementById('cn-wrapper');

    button.addEventListener('click', handler, false);

    function handler(){
        if(!instance.isOpen){
            $('#wrapper-clock').hide();
            this.innerHTML = "Fermer";
            classie.add(wrapper, 'opened-nav');
        }
        else{
            $('#wrapper-clock').show();
            this.innerHTML = "Menu";
            classie.remove(wrapper, 'opened-nav');
        }
        instance.isOpen = !instance.isOpen;
    }

    this.close = function () {
         $('#wrapper-clock').show();
            this.innerHTML = "Menu";
            classie.remove(wrapper, 'opened-nav');
            instance.isOpen = false;
    };

};