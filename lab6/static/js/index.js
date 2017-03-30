var chatBobModalComponent = function() {
	
	var base = this;
	base.form = $("#chatBobModalForm");

	base.init = function() {
		$("#bob-button").click(function(e) {
			e.preventDefault();
			$("#bob-status-message").css("color", "red");

			var user_name = $("#bob-name").val();

			$.ajax({
				url: "/bob",
				type: "POST",
				data: {
					'user_name': user_name
				},
				complete: function(data, status) {
					console.log(data);
					var response = JSON.parse(data.responseText);
					if (Boolean(response.success)) {
						$("#bob-status-message").html = "Handshake Successfully Established.";
						$("#bob-status-message").css("color", "chartreuse");
						$("#bob-status-message").show();
					} else {
						$("#bob-status-message").html = response.error;
						$("#bob-status-message").css("color", "red");
						$("#bob-status-message").show();
					}
				}
			});
		});
	};
};

var mitmModalComponent = function() {
	
	var base = this;
	base.form = $("#mitmModalForm");

	base.init = function() {
		$("#mitm-button").click(function(e) {
			e.preventDefault();
			$("#mitm-status-message").css("color", "red");

			var user_name = $("#mitm-name").val();

			$.ajax({
				url: "/mitm",
				type: "POST",
				data: {
					'user_name': user_name
				},
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
