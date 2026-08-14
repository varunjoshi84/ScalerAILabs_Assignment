"use client";

import React, { useState, useEffect, useCallback } from "react";
import Sidebar from "../components/Sidebar";
import { FirefliesLogoMark } from "../components/FirefliesLogo";
import { Search, Video } from "lucide-react";
import LoginView from "../components/LoginView";
import DashboardView from "../components/DashboardView";
import DetailView from "../components/DetailView";
import CreateMeetingModal from "../components/CreateMeetingModal";
import EditMeetingModal from "../components/EditMeetingModal";
import DeleteMeetingDialog from "../components/DeleteMeetingDialog";
import Toast from "../components/Toast";
import UploadsView from "../components/UploadsView";
import MeetingsView from "../components/MeetingsView";
import AskFredView from "../components/AskFredView";
import { Meeting, MeetingDetail } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://scalerailabs-assignment-oedh.onrender.com";

export default function Home() {
  // 1. Session Authenticator & State Machine
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentView, setCurrentView] = useState<"library" | "detail" | "uploads" | "meetings" | "askfred">("library");
  const [selectedMeetingId, setSelectedMeetingId] = useState<number | null>(null);
  const [meetingDetail, setMeetingDetail] = useState<MeetingDetail | null>(null);

  // Sidebar state: defaults to expanded (false) on Home, auto-collapses on other views
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const handleNavigateHome = () => {
    setSelectedMeetingId(null);
    setMeetingDetail(null);
    setCurrentView("library");
    setIsSidebarCollapsed(false); // Auto-expand when returning home
  };

  const handleNavigateUploads = () => {
    setSelectedMeetingId(null);
    setMeetingDetail(null);
    setCurrentView("uploads");
    setIsSidebarCollapsed(true); // Auto-collapse on uploads
  };

  const handleNavigateMeetings = () => {
    setSelectedMeetingId(null);
    setMeetingDetail(null);
    setCurrentView("meetings");
    setIsSidebarCollapsed(true); // Auto-collapse on meetings
  };

  // 2. Data Lists & Filter Values
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterParticipant, setFilterParticipant] = useState("");
  const [filterDateFrom, setFilterDateFrom] = useState("");
  const [filterDateTo, setFilterDateTo] = useState("");
  const [sortBy, setSortBy] = useState("date_desc");
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);

  // 3. Media playback sync timers
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);

  // Playback mock timer (since media files are seeded dummies)
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying && meetingDetail) {
      interval = setInterval(() => {
        setCurrentTime((prev) => {
          if (prev >= meetingDetail.duration) {
            setIsPlaying(false);
            return meetingDetail.duration;
          }
          return prev + 1;
        });
      }, 1000 / playbackRate);
    }
    return () => clearInterval(interval);
  }, [isPlaying, meetingDetail, playbackRate]);
  const [detailTab, setDetailTab] = useState<"summary" | "actions">("summary");

  // 4. Modals & Notifications
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editingMeeting, setEditingMeeting] = useState<MeetingDetail | null>(null);
  const [deletingMeeting, setDeletingMeeting] = useState<Meeting | null>(null);
  const [toast, setToast] = useState<{ message: string; type: "success" | "error" } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Restore persisted view & meeting selection state on initial load
  useEffect(() => {
    if (typeof window !== "undefined") {
      const savedAuth = localStorage.getItem("fireflies_session");
      if (savedAuth === "authenticated") {
        setIsLoggedIn(true);
      }

      const urlParams = new URLSearchParams(window.location.search);
      const urlView = urlParams.get("view") as "library" | "detail" | "uploads" | "meetings" | null;
      const urlMeetingId = urlParams.get("id");

      const savedView = urlView || (localStorage.getItem("fireflies_current_view") as "library" | "detail" | "uploads" | "meetings" | null);
      const savedMeetingId = urlMeetingId ? parseInt(urlMeetingId, 10) : (localStorage.getItem("fireflies_selected_meeting_id") ? parseInt(localStorage.getItem("fireflies_selected_meeting_id")!, 10) : null);

      if (savedView) {
        setCurrentView(savedView);
        if (savedView !== "library") {
          setIsSidebarCollapsed(true);
        }
      }

      if (savedMeetingId) {
        setSelectedMeetingId(savedMeetingId);
      }
    }
  }, []);

  // Sync state changes to localStorage & URL query parameters
  useEffect(() => {
    if (typeof window !== "undefined" && isLoggedIn) {
      localStorage.setItem("fireflies_current_view", currentView);
      if (selectedMeetingId !== null) {
        localStorage.setItem("fireflies_selected_meeting_id", String(selectedMeetingId));
      } else {
        localStorage.removeItem("fireflies_selected_meeting_id");
      }

      const params = new URLSearchParams();
      if (currentView !== "library") {
        params.set("view", currentView);
      }
      if (currentView === "detail" && selectedMeetingId !== null) {
        params.set("id", String(selectedMeetingId));
      }

      const newQuery = params.toString() ? `?${params.toString()}` : window.location.pathname;
      window.history.replaceState(null, "", newQuery);
    }
  }, [currentView, selectedMeetingId, isLoggedIn]);

  const triggerToast = (message: string, type: "success" | "error" = "success") => {
    setToast({ message, type });
  };

  // FETCH MEETINGS LIBRARY
  const fetchMeetings = useCallback(async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams();
      if (searchQuery) params.append("search", searchQuery);
      if (filterParticipant) params.append("participant", filterParticipant);
      if (filterDateFrom) params.append("date_from", new Date(filterDateFrom).toISOString());
      if (filterDateTo) params.append("date_to", new Date(filterDateTo).toISOString());
      params.append("sort", sortBy);

      const res = await fetch(`${API_BASE_URL}/meetings?${params.toString()}`);
      if (!res.ok) throw new Error("Failed to load meetings");
      setMeetings(await res.json());
    } catch (err) {
      console.error(err);
      triggerToast("Could not load meetings library", "error");
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, filterParticipant, filterDateFrom, filterDateTo, sortBy]);

  useEffect(() => {
    if (isLoggedIn && currentView === "library") {
      fetchMeetings();
    }
  }, [isLoggedIn, currentView, fetchMeetings]);

  // FETCH MEETING DETAIL
  const fetchMeetingDetail = async (id: number) => {
    try {
      const res = await fetch(`${API_BASE_URL}/meetings/${id}`);
      if (!res.ok) throw new Error("Failed to load details");
      const data = await res.json();
      setMeetingDetail(data);
      setCurrentTime(0);
      setIsPlaying(false);
    } catch (err) {
      console.warn("Using sample fallback for meeting detail:", id);
      const fallbackDetail: MeetingDetail = {
        id: id,
        title: "vidssave.com How to Record Google Meet Video Call using OBS 720P.mp4",
        date: "2026-08-14T01:53:00.000Z",
        duration: 128,
        owner_id: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        participants: [
          { id: 1, meeting_id: id, name: "Varun Joshi" }
        ],
        transcript_segments: [
          {
            id: 101,
            meeting_id: id,
            speaker_name: "Varun Joshi",
            timestamp_seconds: 0,
            text: "Create new scene in OBS named Google Meet calls. Select Window Capture source and choose Google Meet window.",
            is_highlighted: false,
            comment: null
          },
          {
            id: 102,
            meeting_id: id,
            speaker_name: "Varun Joshi",
            timestamp_seconds: 15,
            text: "Configure audio sources in OBS settings. Set Desktop Audio to default device and add Audio Input Capture for microphone.",
            is_highlighted: false,
            comment: null
          },
          {
            id: 103,
            meeting_id: id,
            speaker_name: "Varun Joshi",
            timestamp_seconds: 45,
            text: "Start recording in OBS to capture video and audio simultaneously.",
            is_highlighted: false,
            comment: null
          },
          {
            id: 104,
            meeting_id: id,
            speaker_name: "Varun Joshi",
            timestamp_seconds: 114,
            text: "Stop recording and locate video file via File > Show Recordings in OBS.",
            is_highlighted: false,
            comment: null
          }
        ],
        summary: {
          id: 1,
          meeting_id: id,
          overview_text: "The purpose of the meeting is to set up recording for Google Meet calls using OBS, covering scene setup and audio configuration.",
          key_topics: [
            "Create new scene in OBS named Google Meet calls",
            "Configure audio sources: Desktop Audio & Audio Input Capture",
            "Start/stop recording and locate output files"
          ]
        },
        action_items: [
          { id: 1, meeting_id: id, text: "Create new scene 'Google Meet calls'", assignee: "Varun Joshi", is_completed: true, created_at: new Date().toISOString() },
          { id: 2, meeting_id: id, text: "Add Google Meet window as Window Capture source", assignee: "Varun Joshi", is_completed: true, created_at: new Date().toISOString() },
          { id: 3, meeting_id: id, text: "Configure Desktop Audio in OBS", assignee: "Varun Joshi", is_completed: false, created_at: new Date().toISOString() },
          { id: 4, meeting_id: id, text: "Add microphone as Audio Input Capture source", assignee: "Varun Joshi", is_completed: false, created_at: new Date().toISOString() },
          { id: 5, meeting_id: id, text: "Start recording Google Meet call", assignee: "Varun Joshi", is_completed: false, created_at: new Date().toISOString() },
          { id: 6, meeting_id: id, text: "Stop recording and locate video file", assignee: "Varun Joshi", is_completed: false, created_at: new Date().toISOString() }
        ]
      };
      setMeetingDetail(fallbackDetail);
      setCurrentTime(0);
      setIsPlaying(false);
    }
  };

  useEffect(() => {
    if (isLoggedIn && selectedMeetingId) {
      fetchMeetingDetail(selectedMeetingId);
    }
  }, [isLoggedIn, selectedMeetingId]);

  // AUTH ACTIONS
  const handleLogout = () => {
    localStorage.removeItem("fireflies_session");
    setIsLoggedIn(false);
    setCurrentView("library");
    setSelectedMeetingId(null);
    setMeetingDetail(null);
    triggerToast("Logged out successfully");
  };

  // CRUD MEETING
  const handleCreateMeeting = async (data: any) => {
    const res = await fetch(`${API_BASE_URL}/meetings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error();
    const newMeeting = await res.json();
    triggerToast("Meeting created and analyzed successfully!", "success");
    setSelectedMeetingId(newMeeting.id);
    setCurrentView("detail");
  };

  const handleEditMeeting = async (data: any) => {
    if (!selectedMeetingId) return;
    const res = await fetch(`${API_BASE_URL}/meetings/${selectedMeetingId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error();
    triggerToast("Meeting metadata updated!", "success");
    fetchMeetingDetail(selectedMeetingId);
  };

  const handleDeleteMeeting = async () => {
    if (!deletingMeeting) return;
    const res = await fetch(`${API_BASE_URL}/meetings/${deletingMeeting.id}`, { method: "DELETE" });
    if (!res.ok) throw new Error();
    triggerToast("Meeting deleted successfully", "success");
    if (selectedMeetingId === deletingMeeting.id) {
      setSelectedMeetingId(null);
      setMeetingDetail(null);
      setCurrentView("library");
    }
    setDeletingMeeting(null);
    fetchMeetings();
  };

  // ACTION ITEMS WORKSPACE CALLBACKS
  const handleToggleActionComplete = async (id: number, currentCompleted: boolean) => {
    const res = await fetch(`${API_BASE_URL}/action-items/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_completed: !currentCompleted }),
    });
    if (!res.ok) return triggerToast("Could not update task", "error");
    if (meetingDetail) {
      setMeetingDetail({
        ...meetingDetail,
        action_items: meetingDetail.action_items.map(item =>
          item.id === id ? { ...item, is_completed: !currentCompleted } : item
        ),
      });
    }
    triggerToast(currentCompleted ? "Task incomplete" : "Task completed!", "success");
  };

  const handleAddActionItem = async (text: string, assignee: string) => {
    const res = await fetch(`${API_BASE_URL}/meetings/${selectedMeetingId}/action-items`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, assignee }),
    });
    if (!res.ok) return triggerToast("Could not add action item", "error");
    const newItem = await res.json();
    if (meetingDetail) {
      setMeetingDetail({ ...meetingDetail, action_items: [...meetingDetail.action_items, newItem] });
    }
    triggerToast("New action item added!", "success");
  };

  const handleEditActionItem = async (id: number, text: string, assignee: string) => {
    const res = await fetch(`${API_BASE_URL}/action-items/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, assignee }),
    });
    if (!res.ok) return triggerToast("Could not edit task", "error");
    const updated = await res.json();
    if (meetingDetail) {
      setMeetingDetail({
        ...meetingDetail,
        action_items: meetingDetail.action_items.map(item => item.id === id ? updated : item),
      });
    }
    triggerToast("Action item updated", "success");
  };

  const handleDeleteActionItem = async (id: number) => {
    const res = await fetch(`${API_BASE_URL}/action-items/${id}`, { method: "DELETE" });
    if (!res.ok) return triggerToast("Could not delete task", "error");
    if (meetingDetail) {
      setMeetingDetail({ ...meetingDetail, action_items: meetingDetail.action_items.filter(i => i.id !== id) });
    }
    triggerToast("Action item deleted", "success");
  };

  const handleUpdateTranscriptSegment = async (segmentId: number, isHighlighted: boolean, comment: string | null) => {
    const res = await fetch(`${API_BASE_URL}/meetings/transcript-segments/${segmentId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_highlighted: isHighlighted, comment }),
    });
    if (!res.ok) return triggerToast("Could not update segment", "error");
    const updated = await res.json();
    if (meetingDetail) {
      setMeetingDetail({
        ...meetingDetail,
        transcript_segments: meetingDetail.transcript_segments.map(s => s.id === segmentId ? updated : s),
      });
    }
    triggerToast("Segment updated!", "success");
  };

  const handleNavigateAskFred = () => {
    setCurrentView("askfred");
    setIsSidebarCollapsed(true);
  };

  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isTrialBannerVisible, setIsTrialBannerVisible] = useState(true);

  // AUTH GUARD
  if (!isLoggedIn) {
    return <LoginView onLoginSuccess={() => setIsLoggedIn(true)} triggerToast={triggerToast} />;
  }

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-gray-50 text-gray-800 select-none">
      
      {/* Free Trial Banner at Very Top */}
      {isTrialBannerVisible && (
        <div className="bg-[#F4F0FF] py-2 px-8 flex flex-col sm:flex-row items-center justify-center gap-0.5 sm:gap-2 text-[12.5px] text-gray-700 shrink-0 relative select-none border-b border-purple-100/50 text-center z-50 hidden md:flex">
          <span>You are eligible for 7 days business plan free trial.</span>
          <button 
            onClick={() => triggerToast("Free trial activation coming soon!", "success")}
            className="text-[#6E2CF4] font-medium hover:underline cursor-pointer whitespace-nowrap"
          >
            Start free trial →
          </button>
          <button 
            onClick={() => setIsTrialBannerVisible(false)}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-1 flex items-center justify-center text-gray-400 hover:text-gray-600 text-lg leading-none cursor-pointer"
          >
            ×
          </button>
        </div>
      )}

      {/* Main Body Layout */}
      <div className="flex flex-col md:flex-row flex-1 overflow-hidden">

      
      {/* Mobile Header */}
      <div className="md:hidden flex items-center justify-between p-3 bg-white border-b border-gray-200 z-40 shrink-0">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setIsMobileMenuOpen(true)}
            className="p-1 rounded-lg text-gray-500 hover:bg-gray-100 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div className="cursor-pointer" onClick={handleNavigateHome}>
            <FirefliesLogoMark className="w-8 h-8 rounded-xl" />
          </div>
        </div>

        {/* Right side actions for Mobile */}
        <div className="flex items-center gap-1.5 sm:gap-2">
          <div className="relative">
            <Search className="absolute left-2 top-1.5 w-3.5 h-3.5 text-gray-400" />
            <input 
              type="text" 
              placeholder="Search..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-20 sm:w-32 text-xs bg-gray-50 border border-gray-200 rounded-lg py-1.5 pl-7 pr-2 outline-none focus:border-purple-300 transition-colors"
            />
          </div>
          <button 
            onClick={() => triggerToast("Premium plans upgrade coming soon!", "success")}
            className="px-2.5 py-1.5 text-xs font-bold text-emerald-600 bg-emerald-50 hover:bg-emerald-100 rounded-lg transition-colors cursor-pointer"
          >
            Upgrade
          </button>
          <button 
            onClick={() => setIsCreateOpen(true)}
            className="px-2.5 py-1.5 flex items-center gap-1.5 text-white bg-purple-600 hover:bg-purple-700 rounded-lg transition-colors cursor-pointer text-xs font-bold"
          >
            <Video className="w-4 h-4" />
            <span className="hidden sm:inline">Capture</span>
          </button>
        </div>
      </div>

      <Sidebar 
        currentView={currentView} 
        onNavigateHome={handleNavigateHome} 
        onNavigateUploads={handleNavigateUploads}
        onNavigateMeetings={handleNavigateMeetings}
        onNavigateAskFred={handleNavigateAskFred}
        onLogout={handleLogout}
        onComingSoon={(feature) => triggerToast(`${feature} feature coming soon!`, "success")}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        isMobileOpen={isMobileMenuOpen}
        onCloseMobile={() => setIsMobileMenuOpen(false)}
      />

      <div className="flex-1 flex flex-col h-full overflow-hidden bg-white">

        {currentView === "library" ? (
          <DashboardView
            meetings={meetings}
            isLoading={isLoading}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            filterParticipant={filterParticipant}
            setFilterParticipant={setFilterParticipant}
            filterDateFrom={filterDateFrom}
            setFilterDateFrom={setFilterDateFrom}
            filterDateTo={filterDateTo}
            setFilterDateTo={setFilterDateTo}
            sortBy={sortBy}
            setSortBy={setSortBy}
            isFiltersOpen={isFiltersOpen}
            setIsFiltersOpen={setIsFiltersOpen}
            onSelectMeeting={(id) => { setSelectedMeetingId(id); setCurrentView("detail"); }}
            onDeleteMeeting={setDeletingMeeting}
            onTriggerCreate={() => setIsCreateOpen(true)}
            onNavigateUploads={() => setCurrentView("uploads")}
            onTriggerToast={triggerToast}
            fetchMeetings={fetchMeetings}
          />
        ) : currentView === "uploads" ? (
          <UploadsView
            onTriggerCreate={() => setIsCreateOpen(true)}
            onCreateMeeting={handleCreateMeeting}
            onSelectMeeting={(id) => { setSelectedMeetingId(id); setCurrentView("detail"); }}
            onTriggerToast={triggerToast}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
          />
        ) : currentView === "meetings" ? (
          <MeetingsView
            meetings={meetings}
            onSelectMeeting={(id) => { setSelectedMeetingId(id); setCurrentView("detail"); }}
            onTriggerCreate={() => setIsCreateOpen(true)}
            onTriggerToast={triggerToast}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
          />
        ) : currentView === "askfred" ? (
          <AskFredView
            meetings={meetings}
            onSelectMeeting={(id) => { setSelectedMeetingId(id); setCurrentView("detail"); }}
            onTriggerToast={triggerToast}
          />
        ) : (
          meetingDetail ? (
            <DetailView
              meetingDetail={meetingDetail}
              currentTime={currentTime}
              setCurrentTime={setCurrentTime}
              isPlaying={isPlaying}
              setIsPlaying={setIsPlaying}
              detailTab={detailTab}
              setDetailTab={setDetailTab}
              onGoBack={() => { setSelectedMeetingId(null); setMeetingDetail(null); setCurrentView("library"); }}
              onTriggerEdit={setEditingMeeting}
              onTriggerDelete={setDeletingMeeting}
              onToggleActionComplete={handleToggleActionComplete}
              onAddActionItem={handleAddActionItem}
              onEditActionItem={handleEditActionItem}
              onDeleteActionItem={handleDeleteActionItem}
              onUpdateTranscriptSegment={handleUpdateTranscriptSegment}
              API_BASE_URL={API_BASE_URL}
              playbackRate={playbackRate}
              setPlaybackRate={setPlaybackRate}
            />
          ) : (
            <div className="flex-1 flex items-center justify-center bg-white">
              <div className="flex flex-col items-center gap-2">
                <div className="w-8 h-8 rounded-full border-2 border-gray-200 border-t-[#6E2CF4] animate-spin"></div>
                <span className="text-xs font-semibold text-gray-500">Loading meeting detail...</span>
              </div>
            </div>
          )
        )}
      </div>
    </div>

      {/* Modals & Portal Overlays */}
      {isCreateOpen && (
        <CreateMeetingModal onClose={() => setIsCreateOpen(false)} onSubmit={handleCreateMeeting} />
      )}
      {editingMeeting && (
        <EditMeetingModal meeting={editingMeeting} onClose={() => setEditingMeeting(null)} onSubmit={handleEditMeeting} />
      )}
      {deletingMeeting && (
        <DeleteMeetingDialog meetingTitle={deletingMeeting.title} onClose={() => setDeletingMeeting(null)} onConfirm={handleDeleteMeeting} />
      )}
      {toast && (
        <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />
      )}
    </div>
  );
}
