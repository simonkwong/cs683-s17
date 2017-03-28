var chatBobModalComponent = function() {
	
	var base = this;
	base.form = $("#chatBobModalForm");

	base.init = function() {

		$("#generate-keypair").click(function(e) {
			e.preventDefault();

			var RANDOM_PHRASE = "CS683 Security And Privacy.";
			var RSA_BIT_LENGTH = 2048;

			$("#bob-public-key").removeAttr('required');
			$("#bob-private-key").removeAttr('required');

			var userKey = new JSEncrypt({default_key_size: RSA_BIT_LENGTH});
			var userPrivateKey = userKey.getPrivateKey();
			var userPublicKey = userKey.getPublicKey();

			var user_name = $("#bob-name").val();

			if (userPrivateKey != null || userPrivateKey != "", userPublicKey != null || userPublicKey != "") {
				$("#bob-status-message").css('color', 'chartreuse');
				$("#bob-status-message").html("Key Pair Successfully Generated.");

				var userPrivateKeyPemFile = new File([userPrivateKey], user_name + "_private_key.pem", {type: "text/plain;charset=utf-8"});
				saveAs(userPrivateKeyPemFile);

				var userPublicKeyPemFile = new File([userPublicKey], user_name + "_public_key.pem", {type: "text/plain;charset=utf-8"});
				saveAs(userPublicKeyPemFile);
			} else {
				$("#bob-status-message").css('color', 'red');
				$("#bob-status-message").html("Key Pair Generation Unsuccessful.");
				$("#bob-status-message").show();
			}
		});

		$("#bob-button").click(function(e) {
			e.preventDefault();
			$("#bob-status-message").css('color', 'red');
			$("#bob-status-message").html("");
			$("#bob-public-key").attr('required');
			$("#bob-private-key").attr('required');		

			var public_key_file = $('#bob-public-key')[0].files[0];
			var private_key_file = $('#bob-private-key')[0].files[0];
			var bob_public_key_file = $('$bob-bob-public-key')[0].files[0];

			if (public_key_file == null || public_key_file == "" ||
				private_key_file == null || private_key_file == "" ||
				bob_public_key_file == null || bob_public_key_file == "") {
				$("#bob-status-message").html("Please Upload All Keys.");
			}

			var fd = new FormData();
			fd.append('user_name', $("#bob-name").val());
			fd.append('public_key', public_key_file);
			fd.append('private_key', private_key_file);
			fd.append('bob_public_ley', bob_public_key_file);

			$.ajax({
				url: '/upload',
				type: 'POST',
				data: fd,
					contentType: false,
					processData: false,
				complete: function(data, status) {
					console.log(data);
					var response = JSON.parse(data.responseText);
					// if (Boolean(response.success)) {
					// 	window.location = "/home";
					// } else {
					// 	document.getElementById("register-status-message").innerHTML = response.error;
					// 	$("#register-status-message").show();
					// }
				}
			});
		});
	};
};

var mitmModalComponent = function() {
	
	var base = this;
	base.form = $("#mitmModalForm");

	base.init = function() {

		$("#generate-keypair").click(function(e) {
			e.preventDefault();

			var RANDOM_PHRASE = "CS683 Security And Privacy.";
			var RSA_BIT_LENGTH = 2048;

			$("#bob-public-key").removeAttr('required');
			$("#bob-private-key").removeAttr('required');

			var userKey = new JSEncrypt({default_key_size: RSA_BIT_LENGTH});
			var userPrivateKey = userKey.getPrivateKey();
			var userPublicKey = userKey.getPublicKey();

			var user_name = $("#bob-name").val();

			if (userPrivateKey != null || userPrivateKey != "", userPublicKey != null || userPublicKey != "") {
				$("#bob-status-message").css('color', 'chartreuse');
				$("#bob-status-message").html("Key Pair Successfully Generated.");

				var userPrivateKeyPemFile = new File([userPrivateKey], user_name + "_private_key.pem", {type: "text/plain;charset=utf-8"});
				saveAs(userPrivateKeyPemFile);

				var userPublicKeyPemFile = new File([userPublicKey], user_name + "_public_key.pem", {type: "text/plain;charset=utf-8"});
				saveAs(userPublicKeyPemFile);
			} else {
				$("#bob-status-message").css('color', 'red');
				$("#bob-status-message").html("Key Pair Generation Unsuccessful.");
				$("#bob-status-message").show();
			}
		});

		$("#bob-button").click(function(e) {
			e.preventDefault();
			$("#bob-status-message").css('color', 'red');
			$("#bob-status-message").html("");
			$("#bob-public-key").attr('required');
			$("#bob-private-key").attr('required');		

			var public_key_file = $('#bob-public-key')[0].files[0];
			var private_key_file = $('#bob-private-key')[0].files[0];
			var bob_public_key_file = $('$bob-bob-public-key')[0].files[0];

			if (public_key_file == null || public_key_file == "" ||
				private_key_file == null || private_key_file == "" ||
				bob_public_key_file == null || bob_public_key_file == "") {
				$("#bob-status-message").html("Please Upload All Keys.");
			}

			var fd = new FormData();
			fd.append('user_name', $("#bob-name").val());
			fd.append('public_key', public_key_file);
			fd.append('private_key', private_key_file);
			fd.append('bob_public_ley', bob_public_key_file);

			$.ajax({
				url: '/upload',
				type: 'POST',
				data: fd,
					contentType: false,
					processData: false,
				complete: function(data, status) {
					console.log(data);
					var response = JSON.parse(data.responseText);
					// if (Boolean(response.success)) {
					// 	window.location = "/home";
					// } else {
					// 	document.getElementById("register-status-message").innerHTML = response.error;
					// 	$("#register-status-message").show();
					// }
				}
			});
		});
	};
};


$(document).ready(function() {

	var chatBobModalComponent_ = new chatBobModalComponent();
	chatBobModalComponent_.init();

	$("#chatBobModal").on("shown.bs.modal", function() {
		$("#bob-name").focus();
	});

	$("#chatBobModal").on("hidden.bs.modal", function() {
		$("#bob-status-message").hide();
	});

	$("#mitmModal").on("shown.bs.modal", function() {
		$("#mitm-name").focus();
	});

	$("#mitmModal").on("hidden.bs.modal", function() {
		$("#mitm-status-message").hide();
	});
});