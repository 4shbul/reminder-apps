// Menampilkan notifikasi pada browser
function showNotification(title, body) {
    if (Notification.permission === "granted") {
        new Notification(title, { body: body });
    } else {
        alert("Pengingat: " + body);
    }
}

// Meminta izin untuk pemberitahuan browser
if (Notification.permission !== "granted") {
    Notification.requestPermission();
}
