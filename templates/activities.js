function onActivityHoverIn(similar_activities) {
    for (var id of similar_activities) {
        var activity = document.getElementById(id);
        activity.classList.add("bg-yellow-500");
        activity.classList.add("hover:bg-gray-700");
    }
}

function onActivityHoverOut(similar_activities) {
    for (var id of similar_activities) {
        var activity = document.getElementById(id);
        activity.classList.remove("bg-yellow-500");
        activity.classList.remove("hover:bg-gray-700");
    }
}

function openActivityPage(activity_id) {
    window.open(`https://connect.garmin.com/modern/activity/${activity_id}`, "_blank");
}
