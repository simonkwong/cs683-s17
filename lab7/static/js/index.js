var resigterModalComponent = function() {
	
	var base = this;
	base.form = $("#registerModalForm");

	base.init = function() {

		$("#generate-keypair").click(function(e) {
			e.preventDefault();

			var RANDOM_PHRASE = "CS683 Security And Privacy.";
			var RSA_BIT_LENGTH = 2048;

			$("#register-public-key").removeAttr('required');
			$("#register-username").removeAttr('required');
			$("#register-password").removeAttr('required');
			$("#confirm-password").removeAttr('required');


			var userKey = new JSEncrypt({default_key_size: RSA_BIT_LENGTH});
			var userPrivateKey = userKey.getPrivateKey();
			var userPublicKey = userKey.getPublicKey();

			if (userPrivateKey != null || userPrivateKey != "", userPublicKey != null || userPublicKey != "") {
				document.getElementById("register-status-message").style.color = "chartreuse";
				document.getElementById("register-status-message").innerHTML = "Key Pair Successfully Generated.";

				var userPrivateKeyPemFile = new File([userPrivateKey], "user_private_key.pem", {type: "text/plain;charset=utf-8"});
				saveAs(userPrivateKeyPemFile);

				var userPublicKeyPemFile = new File([userPublicKey], "user_public_key.pem", {type: "text/plain;charset=utf-8"});
				saveAs(userPublicKeyPemFile);
			} else {
				document.getElementById("register-status-message").style.color = "red";
				document.getElementById("register-status-message").innerHTML = "Key Pair Generation Unsuccessful.";
				$("#register-status-message").show();
			}
		});

		$("#register-button").click(function(e) {
			e.preventDefault();
			document.getElementById("register-status-message").innerHTML = '';
			document.getElementById("register-status-message").style.color = "red";
			$("#register-public-key").attr('required');
			$("#register-username").attr('required');
			$("#register-password").attr('required');
			$("#confirm-password").attr('required');			

			var username = document.getElementById("register-username").value;
			var password = document.getElementById("register-password").value;
			var confirm_password = document.getElementById("confirm-password").value;
			var public_key_file = $('#register-public-key')[0].files[0];

			var hashed_password = sha512(password);

			if (username == null || password == null || confirm_password == null || public_key_file == null ||
				username == "" || password == "" || confirm_password == "" || public_key_file == "") {
				document.getElementById("register-status-message").innerHTML = "All Fields Are Required.";
			}

			var fd = new FormData();
			fd.append('public_key', public_key_file);
			fd.append('username', username);
			fd.append('password', hashed_password);

			if (password != confirm_password) {
				document.getElementById("register-status-message").innerHTML = "Passwords Don't Match.";
				$("#register-status-message").show();
			} else {
				$.ajax({
	                url: '/register',
	                type: 'POST',
	                data: fd,
  					contentType: false,
  					processData: false,
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
			var private_key_file = $('#add-private-key')[0].files[0];

			var hashed_password = sha512(password);
			
			var fd = new FormData();
			fd.append('private_key', private_key_file);
			fd.append('username', username);
			fd.append('password', hashed_password);

			$.ajax({
                url: "/login",
                type: 'POST',
                data: fd,
                contentType: false,
  				processData: false,
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

var SERVER_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----\
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA8JsF6x8wEoegggMP1mg5\
ssQOGXNk2OADrPx5gJY+N2/8DYgc8N2IxTR65d3g7yoloXFcWlyBkdJMt50ugKG/\
66bJ+9Wb2I7teYoSMXTbhJ0H1Tzmr+aY3M8hSqy8KlT3QEmBwE4izwrO0qfFPXcG\
kGz+UbKeBs5tL+0cP5AGdj1qFgqrElS+QddPa4R/KNnhoIQKzScCN5WOda82ccQs\
x57B1+JiFk0WPo97p8pBGwpNxaR6rdmeb4b2amf4X0tdsWDVEsDIdnNzfxzmGfAT\
4205p+iv08KSDAH1qnh9JKUjsy1fhw/W+P34fO1WPer4jc2/2EGyBQY3SeOuhQEI\
7wIDAQAB\
-----END PUBLIC KEY-----"