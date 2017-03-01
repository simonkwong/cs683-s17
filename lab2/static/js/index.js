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
                    username: username,
                    password: hashed_password 
                },
                complete: function(data, status) {
                	console.log(data);
                	var response = JSON.parse(data.statusText);
					if (Boolean(response.success)) {
						window.location = "/home";
					} else {
						document.getElementById("login-status-message").innerHTML = response.error;
					}
                }
			});
		});
	};
};

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
			
			var userPrivateKey = cryptico.generateRSAKey(RANDOM_PHRASE, RSA_BIT_LENGTH);
			var userPublicKey = cryptico.publicKeyString(userPrivateKey);
			userPrivateKey = userPrivateKey.getPrivateKey();
			userPublicKey = "-----BEGIN PUBLIC KEY-----\r\n" + userPublicKey + "\r\n-----END PUBLIC KEY-----";

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
			} else {
				$.ajax({
	                url: '/register',
	                type: 'POST',
	                data: fd,
  					contentType: false,
  					processData: false,
	                complete: function(data, status) {
	                	console.log(data);
	                	var response = JSON.parse(data.statusText);
						if (Boolean(response.success)) {
							window.location = "/home";
						} else {
							document.getElementById("register-status-message").innerHTML = response.error;
						}
	                }
				});
			};
		});
	};
};

var privateKeyString = function(rsakey) {
	var parametersBigint = ["n", "d", "p", "q", "dmp1", "dmq1", "coeff"];
    var keyObj = {};
    parametersBigint.forEach(function(parameter){
        keyObj[parameter] = cryptico.b16to64(rsakey[parameter].toString(16));
    });
    return JSON.stringify(keyObj);
}	

$(document).ready(function() {

	var loginModalComponent_ = new loginModalComponent();
	loginModalComponent_.init();

	var resigterModalComponent_ = new resigterModalComponent();
	resigterModalComponent_.init();

});