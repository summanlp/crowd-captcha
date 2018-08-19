if("undefined" === typeof jQuery)
    throw new Error("Sin jQuery no vivimos!");

// https://stackoverflow.com/a/16349647
String.prototype.toDOM = function() {
  var d =
      document,
      i,
      a=d.createElement("div"),
      b=d.createDocumentFragment();
  a.innerHTML=this;
  while(i=a.firstChild)b.appendChild(i);
  return b;
};

function createModal() {
    return `
        {{modal}}
    `.toDOM();
}

function createButton() {
    var btn = document.createElement("button");
    var t = document.createTextNode("No soy un robot!");
    btn.appendChild(t);
    btn.setAttribute("id", "captcha-validate");
    btn.setAttribute("type", "button");
    btn.setAttribute("class", "btn");
    return btn;
}

function disableFormSubmission(form) {
    form.submit(function (e) {
        e.preventDefault();
    });
}

function enableFormSubmission(form) {
    form.unbind('submit').submit();
}

function bindModalDismiss(form, modal) {
    $(document).on("click", "#send-captcha", function() {
        $("#captcha-mod").modal("hide");
        enableFormSubmission(form)
    });
}

function configureModal(button) {
    $(button).click(function () {
        $("#captcha-mod").modal({
            backdrop: 'static',
            keyboard: false
        });
    });
}

(function($) {
    $(function() {
        let captcha = document.getElementById("captcha");
        let form = $('#captcha').closest("form");
        disableFormSubmission(form);

        let button = createButton();
        captcha.appendChild(button);

        let modal = createModal();
        configureModal(button);
        document.body.appendChild(modal);
        bindModalDismiss(form, modal);
    });
})(jQuery);