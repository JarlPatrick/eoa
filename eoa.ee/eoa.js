function findperson(){
	if (document.getElementById('NIF').value != '') {
		var address = '/?name=' + document.getElementById('NIF').value;
		location.href = address;
	}
}

function search(ele) {
	if (event.key === 'Enter') {
		findperson();
	}
}

var openPanels;
const panelKey = "sidenav-open-panels";
const sidenavOpenKey = "sidenav-open";
const sidenavScrollKey = "sidenav-scroll";
var sidenavRoot;

/* Set the width of the side navigation to 250px and the left margin of the page content to 250px, save the state */
function openNav() {
	document.getElementById("mySidenav").style.width = "400px";
	document.getElementById("main").style.marginLeft = "400px";
	sessionStorage.setItem(sidenavOpenKey, "1");
}

/* Set the width of the side navigation to 0 and the left margin of the page content to 0, save the state */
function closeNav() {
	document.getElementById("mySidenav").style.width = "0";
	document.getElementById("main").style.marginLeft = "0";
	sessionStorage.setItem(sidenavOpenKey, "");
}

function initnav(){
	sidenavRoot = document.getElementById("mySidenav");
	var acc = document.getElementsByClassName("accordion");
	var i;
	for (i = 0; i < acc.length; i++) {
		acc[i].addEventListener("click", function () {
			/* Toggle between adding and removing the "active" class,
			to highlight the button that controls the panel */
			this.classList.toggle("active");

			/* Toggle between hiding and showing the active panel */
			var panel = this.nextElementSibling;
			if (panel.style.display === "block") {
				panel.style.display = "none";
				openPanels.delete(panel.id);
			} else {
				panel.style.display = "block";
				openPanels.add(panel.id);
			}

			/* Update open panels */
			sessionStorage.setItem(panelKey, JSON.stringify([...openPanels]));
		});
	}

	/* Load open panels (none on first load) */
	if(!sessionStorage.getItem(panelKey)) {
		sessionStorage.setItem(panelKey, "[]");
	}
	openPanels = new Set(JSON.parse(sessionStorage.getItem(panelKey)));
	openPanels.forEach(id => {
		const el = document.getElementById(id);
		if(el) {
			el.style.display = "block";
			el.previousElementSibling.classList.toggle("active");
		}
	});

	/* Load menu open/closed state (closed on first load) */
	if(sessionStorage.getItem(sidenavOpenKey)) {
		openNav();
	}

	/* Load menu scroll (0 on first load) */
	if(!sessionStorage.getItem(sidenavScrollKey)) {
		sessionStorage.setItem(sidenavScrollKey, 0);
	}
	sidenavRoot.scrollTop = sessionStorage.getItem(sidenavScrollKey);
	sidenavRoot.addEventListener("scroll", function() {
		sessionStorage.setItem(sidenavScrollKey, sidenavRoot.scrollTop);
	});
}
