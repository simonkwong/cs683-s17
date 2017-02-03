var loginModalComponent = function() {

	var base = this;
	base.form = $("#loginModalForm");

	base.init = function() {
		$("#login-button").click(function() {


			var username = document.getElementById("login-username").value;
			var password = document.getElementById("login-password").value;

			$.ajax({
                url: window.location.pathname + "/login",
                type: 'POST',
                data: {
                    username: username,
                    password: password 
                },
                complete: function(data, status) {
                    if (status == "success") {
                        location.reload();
                    } else {
                        alert("Something went wrong during the login.");
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
		$("#register-button").click(function() {

			var username = document.getElementById("register-username").value;
			var password = document.getElementById("register-password").value;
			var confirm_password = document.getElementById("confirm-password").value;

			if (password != confirm_password) {
				alert("Passwords Don't Match."); 
			} else {

				$.ajax({
	                url: "/register",
	                type: 'POST',
	                data: {
	                    username: username,
	                    password: password            
	                },
	                complete: function(data, status) {
	                    if (status == "success") {
	                		window.location = "/home";
	                    } else {
	                        alert("Something went wrong during registration.");
	                    }
	                }
				});
			};
		});
	};
};


$(document).ready(function() {

	var loginModalComponent_ = new loginModalComponent();
	loginModalComponent_.init();

	var resigterModalComponent_ = new resigterModalComponent();
	resigterModalComponent_.init();

});