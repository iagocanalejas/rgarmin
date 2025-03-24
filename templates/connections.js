function onConfirmSelectionClick() {
    const url = new URL("/activities", window.location.origin);
    for (card of document.querySelectorAll(".bg-green-500")) {
        url.searchParams.append("connections", card.id);
    }
    window.location.href = url.toString();
}

function toggleCard(card) {
    card.classList.toggle("bg-green-500");
    card.classList.toggle("hover:bg-gray-700");
}
