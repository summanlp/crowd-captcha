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

clickedSliders = new Set();

function clickSlider(id) {
	clickedSliders.add(id);
	if(clickedSliders.size == {{num_questions}})
		$("#send-captcha").removeAttr("disabled");
}

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

function getUserId() {
    // TODO: do something if user didn't complete this?.
    return $(".captcha-user-id").val();
}

function getTags() {
    return $("output.captcha-question").map(function(i, e) {
        return {
            text_uuid: e.id.replace("slider_output_id_", "").replace(/_/g, "-"),
            tag: e.value,
        };
    }).toArray();
}

function bindModalDismiss(form) {
    $(document).on("click", "#send-captcha", function() {
        $.ajax({
            url: "{{ get_endpoint_route('tag') }}",
            data: JSON.stringify({
                app_uuid: "{{ app_uuid }}",
                user_id: getUserId(),
                tags: getTags(),
            }),
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            type: "POST",
            success: function(data) {
                onTagSuccess(form, data.secret);
            },
            error: onTagError,
        });
    });
}

function addSecretToForm(form, secret) {
    let input = document.createElement("input");
    input.setAttribute("type", "hidden");
    input.setAttribute("name", "captcha_secret");
    input.setAttribute("value", secret);
    form.append(input);
}

function onTagSuccess(form, secret) {
    $("#captcha-mod").modal("hide");
    enableFormSubmission(form);
    addSecretToForm(form, secret);
}

function onTagError() {
    // TODO: implement me.
    alert("Error! Seguro sos un bot");
}

function configureModal(button) {
    $(button).click(function () {
        $("#captcha-mod").modal();
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
        bindModalDismiss(form);
    });
})(jQuery);
