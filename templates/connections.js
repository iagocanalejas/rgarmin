function getSelectedConnections() {
    const selectedConnectionIds = [];
    for (card of document.querySelectorAll(".bg-green-500")) {
        selectedConnectionIds.push(card.id);
    }
    return selectedConnectionIds;
}

function toggleCard(card) {
    card.classList.toggle("bg-green-500");
    card.classList.toggle("hover:bg-gray-700");
}
