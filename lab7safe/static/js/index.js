var resigterModalComponent = function() {
	
	var base = this;
	base.form = $("#registerModalForm");

	base.init = function() {

		$("#register-button").click(function(e) {
			e.preventDefault();
			document.getElementById("register-status-message").innerHTML = '';
			document.getElementById("register-status-message").style.color = "red";
			$("#register-username").attr('required');
			$("#register-password").attr('required');
			$("#confirm-password").attr('required');			

			var username = document.getElementById("register-username").value;
			var password = document.getElementById("register-password").value;
			var confirm_password = document.getElementById("confirm-password").value;

			var hashed_password = sha512(password);

			if (username == null || password == null || confirm_password == null ||
				username == "" || password == "" || confirm_password == "") {
				document.getElementById("register-status-message").innerHTML = "All Fields Are Required.";
			}

			if (password != confirm_password) {
				document.getElementById("register-status-message").innerHTML = "Passwords Don't Match.";
				$("#register-status-message").show();
			} else {
				$.ajax({
	                url: '/register',
	                type: 'POST',
	                data: {
	                	"username": username,
	                	"password": password
	                },
	                complete: function(data, status) {
	                	console.log(data);
	                	var response = JSON.parse(data.responseText);
						if (Boolean(response.success)) {
							window.location = "/home";
						} else {
							document.getElementById("register-status-message").innerHTML = response.error;
							$("#register-status-message").show();
						}
	                }
				});
			};
		});
	};
};

var loginModalComponent = function() {

	var base = this;
	base.form = $("#loginModalForm");

	base.init = function() {
		$("#login-button").click(function(e) {
			e.preventDefault();

			var username = document.getElementById("login-username").value;
			var password = document.getElementById("login-password").value;

			var hashed_password = sha512(password);

			$.ajax({
                url: "/login",
                type: 'POST',
                data: {
                	"username": username,
                	"password": password
                },
                complete: function(data, status) {
                	console.log(data);
                	var response = JSON.parse(data.responseText);
					if (Boolean(response.success)) {
						window.location = "/home";
					} else {
						document.getElementById("login-status-message").innerHTML = response.error;
						$("#login-status-message").show();
					}
                }
			});
		});
	};
};	

$(document).ready(function() {

	var loginModalComponent_ = new loginModalComponent();
	loginModalComponent_.init();

	var resigterModalComponent_ = new resigterModalComponent();
	resigterModalComponent_.init();

	$("#registerModal").on("shown.bs.modal", function() {
        $("#register-username").focus();
    });

    $("#registerModal").on("hidden.bs.modal", function() {
        $("#register-status-message").hide();
	});

	$("#loginModal").on("shown.bs.modal", function() {
        $("#login-username").focus();
    });

    $("#loginModal").on("hidden.bs.modal", function() {
        $("#login-status-message").hide();
    });
});