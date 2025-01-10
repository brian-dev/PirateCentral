/* global bootstrap */
document.addEventListener("DOMContentLoaded", () => {
  // 1) Restore previously active conference tab
  const savedConferenceTab = localStorage.getItem("activeConferenceTab");
  if (savedConferenceTab) {
    const conferenceTabTrigger = document.querySelector(
      `#conferenceTabs button[data-bs-target="${savedConferenceTab}"]`
    );
    if (conferenceTabTrigger) {
      new bootstrap.Tab(conferenceTabTrigger).show();
    }
  }

  // 2) Restore region tabs
  const allRegionTabLists = document.querySelectorAll('[id^="regionTabs"]');
  allRegionTabLists.forEach((regionTabList) => {
    const regionListId = regionTabList.id;
    const savedRegionTab = localStorage.getItem(`activeRegionTab-${regionListId}`);
    if (savedRegionTab) {
      const regionTabTrigger = regionTabList.querySelector(
        `button[data-bs-target="${savedRegionTab}"]`
      );
      if (regionTabTrigger) {
        new bootstrap.Tab(regionTabTrigger).show();
      }
    }
  });

  // 3) Now that we've applied any saved tabs, remove the hidden class
  const tabContentContainers = document.querySelectorAll('.tab-content.hidden-tabs');
  tabContentContainers.forEach((container) => {
    container.classList.remove('hidden-tabs');
  });

  // 4) Add event listeners to save active tab
  const conferenceTabButtons = document.querySelectorAll('#conferenceTabs button[data-bs-toggle="tab"]');
  conferenceTabButtons.forEach((btn) => {
    btn.addEventListener("shown.bs.tab", (event) => {
      localStorage.setItem("activeConferenceTab", event.target.dataset.bsTarget);
    });
  });

  allRegionTabLists.forEach((regionTabList) => {
    const regionListId = regionTabList.id;
    const regionTabButtons = regionTabList.querySelectorAll('button[data-bs-toggle="tab"]');
    regionTabButtons.forEach((btn) => {
      btn.addEventListener("shown.bs.tab", (event) => {
        localStorage.setItem(`activeRegionTab-${regionListId}`, event.target.dataset.bsTarget);
      });
    });
  });
});
