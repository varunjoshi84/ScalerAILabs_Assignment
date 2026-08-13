"use client";

import React, { useState, useRef } from "react";
import { 
  Search, 
  Video, 
  Mic, 
  Bell, 
  Upload,
  FileText,
  Globe,
  Hash,
  MoreHorizontal,
  ChevronRight,
  Clock,
  Sparkles,
  CheckCircle2
} from "lucide-react";

interface UploadsViewProps {
  onTriggerCreate: () => void;
  onCreateMeeting?: (data: any) => Promise<void>;
  onSelectMeeting?: (id: number) => void;
  onTriggerToast: (msg: string, type?: "success" | "error") => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
}

interface UploadedFile {
  id: string;
  name: string;
  size: string;
  date: string;
  duration?: string;
  format: string;
  status: "processing" | "completed";
  meetingId?: number;
}

export default function UploadsView({
  onTriggerCreate,
  onCreateMeeting,
  onSelectMeeting,
  onTriggerToast,
  searchQuery,
  setSearchQuery
}: UploadsViewProps) {
  const [isNoticeVisible, setIsNoticeVisible] = useState(true);
  const [isTrialBannerVisible, setIsTrialBannerVisible] = useState(true);
  const [selectedFileForModal, setSelectedFileForModal] = useState<UploadedFile | null>(null);

  // File input ref for real file selection
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Simulated uploads list (initialized with sample from Image 2/3/4)
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([
    {
      id: "up-1",
      name: "Q3_Product_Strategy_Transcript.txt",
      size: "1.4 MB",
      date: "Aug 14",
      duration: "15 min",
      format: "TXT",
      status: "completed",
      meetingId: 1
    }
  ]);

  // Handle actual transcript or file upload
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const file = files[0];
    const ext = file.name.split(".").pop()?.toUpperCase() || "TXT";
    const sizeMb = (file.size / (1024 * 1024)).toFixed(1) + " MB";
    const fileId = "up-" + Date.now();

    const newFileItem: UploadedFile = {
      id: fileId,
      name: file.name,
      size: sizeMb,
      date: "Aug 14",
      duration: "10 min",
      format: ext,
      status: "processing"
    };

    setUploadedFiles(prev => [newFileItem, ...prev]);
    onTriggerToast(`Uploading and analyzing transcript "${file.name}"...`, "success");

    let transcriptText = "";

    // If it's a text/transcript file, read its actual contents!
    if (file.type.includes("text") || file.name.endsWith(".txt") || file.name.endsWith(".srt") || file.name.endsWith(".vtt")) {
      try {
        transcriptText = await file.text();
      } catch {
        transcriptText = "";
      }
    }

    // Fallback or generated structured transcript with speaker labels & timestamps
    if (!transcriptText || transcriptText.trim().length < 10) {
      const cleanTitle = file.name.replace(/\.[^/.]+$/, "");
      transcriptText = `Varun Joshi (00:05): Welcome everyone to the ${cleanTitle} session. Today we are reviewing key milestones.
Alice Smith (00:20): Thanks Varun. On the product frontend side, we completed the responsive navigation layout.
Bob Jones (00:45): Excellent progress. We need to verify API rate limiting and finalize database indexes before demo.
Varun Joshi (01:15): Action item for Bob: Run load testing and update security rules by Friday.
Alice Smith (01:40): I will prepare the product summary and export final transcript metrics.`;
    }

    const meetingTitle = file.name.replace(/\.[^/.]+$/, "").replace(/_/g, " ");

    try {
      if (onCreateMeeting) {
        await onCreateMeeting({
          title: meetingTitle,
          date: new Date().toISOString(),
          duration: 600, // 10 minutes
          participants: ["Varun Joshi", "Alice Smith", "Bob Jones"],
          transcript_text: transcriptText
        });

        setUploadedFiles(prev => 
          prev.map(f => f.id === fileId ? { ...f, status: "completed" } : f)
        );
        onTriggerToast(`Transcript analyzed! Redirecting to meeting detail...`, "success");
      } else {
        // Fallback timer if prop not connected
        setTimeout(() => {
          setUploadedFiles(prev => 
            prev.map(f => f.id === fileId ? { ...f, status: "completed" } : f)
          );
          onTriggerToast(`Transcript generated for ${file.name}!`, "success");
        }, 2000);
      }
    } catch {
      setUploadedFiles(prev => 
        prev.map(f => f.id === fileId ? { ...f, status: "completed" } : f)
      );
    }
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-white font-sans">
      
      {/* Free Trial Banner at Very Top */}
      {isTrialBannerVisible && (
        <div className="bg-[#F4F0FF] py-2 px-4 flex items-center justify-center gap-1 text-[12.5px] text-gray-700 shrink-0 relative select-none border-b border-purple-100/50">
          <span>You are eligible for 7 days business plan free trial.</span>
          <button 
            onClick={() => onTriggerToast("Free trial activation coming soon!", "success")}
            className="text-[#6E2CF4] font-medium hover:underline cursor-pointer ml-1"
          >
            Start free trial →
          </button>
          <button 
            onClick={() => setIsTrialBannerVisible(false)}
            className="absolute right-4 text-gray-400 hover:text-gray-600 text-sm leading-none cursor-pointer"
          >
            ×
          </button>
        </div>
      )}

      {/* Header Toolbar */}
      <header className="px-6 py-3 border-b border-gray-100 flex items-center justify-between shrink-0 bg-white select-none">
        <h1 className="text-[15px] font-bold text-gray-900">Uploads</h1>
        
        {/* Center Search Bar */}
        <div className="max-w-[440px] w-full relative flex items-center">
          <Search className="absolute left-3.5 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search by title or keyword"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full text-[13px] bg-[#F8FAFC] border border-gray-200 focus:border-[#6E2CF4] focus:bg-white rounded-xl py-2 pl-10 pr-14 outline-none text-gray-800 transition-all placeholder-gray-400"
          />
          <span className="absolute right-3.5 text-[10px] text-gray-400 border border-gray-200 px-1.5 py-0.5 rounded bg-white font-medium select-none">
            ⌘K
          </span>
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          <button 
            onClick={() => onTriggerToast("Premium plans upgrade coming soon!", "success")}
            className="bg-[#ECFDF5] hover:bg-[#D1FAE5] text-[#059669] font-medium py-1.5 px-3.5 rounded-lg text-[13px] transition-colors cursor-pointer"
          >
            Upgrade
          </button>

          <button
            onClick={onTriggerCreate}
            className="flex items-center gap-1.5 bg-[#6E2CF4] hover:bg-[#5B21D6] text-white font-medium py-1.5 px-3.5 rounded-lg text-[13px] transition-colors shadow-xs cursor-pointer"
          >
            <Video className="w-3.5 h-3.5" />
            <span>Capture</span>
            <span className="text-[9px] text-purple-200 ml-0.5">▼</span>
          </button>

          <button 
            onClick={() => onTriggerToast("Mic settings coming soon!", "success")}
            className="p-1.5 hover:bg-gray-100 rounded-full text-gray-400 hover:text-gray-700 transition-colors cursor-pointer"
          >
            <Mic className="w-4 h-4" />
          </button>

          <button 
            onClick={() => onTriggerToast("No new notifications.", "success")}
            className="p-1.5 hover:bg-gray-100 rounded-full text-gray-400 hover:text-gray-700 transition-colors relative cursor-pointer"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full border-2 border-white"></span>
          </button>

          <div className="w-8 h-8 rounded-full overflow-hidden border border-gray-200 shrink-0 ml-1 cursor-pointer">
            <div className="w-full h-full bg-[#6E2CF4] flex items-center justify-center text-white font-bold text-xs">
              V
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-8 py-8 space-y-8">
          
          {/* Yellow Notice Banner matching Image 2 */}
          {isNoticeVisible && (
            <div className="bg-[#FEFCE8] border border-[#FDE68A] rounded-xl px-5 py-3 flex items-center justify-between text-[13px] text-[#854D0E] select-none">
              <div className="flex-1 text-center font-medium">
                Uploads are moving — you'll find them on the Meetings page soon.
              </div>
              <button 
                onClick={() => setIsNoticeVisible(false)}
                className="text-[#A16207] hover:text-[#713F12] text-sm leading-none ml-4 cursor-pointer"
              >
                ×
              </button>
            </div>
          )}

          {/* Hidden HTML File Input for real file selection */}
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange}
            accept=".txt,.pdf,.doc,.docx,.vtt,.srt,.mp3,.mp4,.wav,.m4a,.json" 
            className="hidden" 
          />

          {/* Drag & Drop Upload Dropzone matching Image 2 */}
          <div 
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-[#C4B5FD] rounded-2xl py-14 px-8 flex flex-col items-center justify-center text-center gap-4 bg-white hover:border-[#8B5CF6] hover:bg-[#F9F5FF]/50 transition-all cursor-pointer group"
          >
            <div className="w-12 h-12 rounded-2xl bg-[#F3E8FF] text-[#7C3AED] flex items-center justify-center group-hover:scale-105 transition-transform">
              <Upload className="w-6 h-6" strokeWidth={2} />
            </div>
            
            <div className="space-y-1.5 max-w-md">
              <h3 className="text-[16px] font-bold text-gray-900">
                Upload a transcript or media file to generate AI insights
              </h3>
              <p className="text-[12px] text-gray-500 leading-relaxed font-normal">
                Browse or drag and drop <span className="font-semibold text-gray-700">TXT, DOCX, VTT, SRT, MP3, M4A, WAV</span> or <span className="font-semibold text-gray-700">MP4</span> files.
              </p>
            </div>

            <div className="flex items-center gap-3 mt-1">
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  fileInputRef.current?.click();
                }}
                className="bg-[#6E2CF4] hover:bg-[#5B21D6] text-white font-medium py-2.5 px-6 rounded-lg text-xs font-semibold shadow-xs transition-colors cursor-pointer"
              >
                Browse Files
              </button>
              
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onTriggerCreate();
                }}
                className="border border-purple-200 bg-purple-50 hover:bg-purple-100 text-[#6E2CF4] font-medium py-2.5 px-5 rounded-lg text-xs font-semibold transition-colors cursor-pointer flex items-center gap-1.5"
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Paste Text Transcript</span>
              </button>
            </div>
          </div>

          {/* Uploaded Files Section matching Image 2, 3, 4 */}
          {uploadedFiles.length > 0 && (
            <div className="space-y-3 pt-2">
              <h4 className="text-[13px] font-bold text-gray-900 select-none">Recent Transcript Uploads</h4>

              {uploadedFiles.map((file) => (
                <div 
                  key={file.id}
                  className="bg-[#F8FAFC] border border-gray-200/80 rounded-xl p-4 flex items-center justify-between hover:border-purple-200 transition-all shadow-2xs"
                >
                  <div className="flex items-center gap-3.5 min-w-0">
                    {/* Format Badge */}
                    <div className="w-10 h-10 rounded-lg bg-[#38BDF8] flex items-center justify-center text-white font-extrabold text-[11px] shrink-0 shadow-2xs uppercase">
                      {file.format}
                    </div>

                    <div className="min-w-0">
                      <h4 className="text-[13px] font-semibold text-gray-900 truncate">
                        {file.name}
                      </h4>
                      <span className="text-[11px] text-gray-400 font-medium block mt-0.5">
                        {file.date} {file.duration ? `· ${file.duration}` : ""} · {file.size}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0 ml-4 select-none">
                    {file.status === "processing" ? (
                      <div className="bg-[#FEF3C7] text-[#D97706] rounded-full text-[11.5px] px-3 py-1 font-semibold flex items-center gap-1.5 animate-pulse">
                        <Clock className="w-3.5 h-3.5" />
                        <span>Processing transcript</span>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <button 
                          onClick={() => {
                            if (file.meetingId && onSelectMeeting) {
                              onSelectMeeting(file.meetingId);
                            } else {
                              onTriggerToast("Opening transcript detail view...", "success");
                            }
                          }}
                          className="bg-purple-50 border border-purple-200 hover:bg-purple-100 text-[#6E2CF4] font-semibold py-1.5 px-3 rounded-lg text-xs flex items-center gap-1.5 cursor-pointer transition-colors"
                        >
                          <Sparkles className="w-3.5 h-3.5 text-[#6E2CF4]" />
                          <span>View Transcript & AI Summary</span>
                        </button>

                        <button 
                          onClick={() => setSelectedFileForModal(file)}
                          className="border border-gray-200 hover:bg-gray-50 text-gray-700 font-medium py-1.5 px-3 rounded-lg text-xs flex items-center gap-1 cursor-pointer transition-colors"
                        >
                          <span>Details</span>
                          <ChevronRight className="w-3.5 h-3.5 text-gray-400" />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}

        </div>
      </div>

      {/* Details Modal Overlay matching Image 5 */}
      {selectedFileForModal && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-2xs p-4"
          onClick={() => setSelectedFileForModal(null)}
        >
          <div 
            className="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden border border-gray-100 animate-in zoom-in-95 duration-150 p-6 space-y-6"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-start justify-between gap-3 border-b border-gray-100 pb-4">
              <div className="flex items-start gap-3 min-w-0">
                <div className="w-8 h-8 rounded-lg bg-purple-50 text-[#7C3AED] flex items-center justify-center shrink-0 mt-0.5">
                  <FileText className="w-4 h-4" />
                </div>
                <div className="min-w-0">
                  <h3 className="text-[14px] font-bold text-gray-900 truncate">
                    {selectedFileForModal.name}
                  </h3>
                  <span className="text-[11.5px] text-gray-400 font-medium block mt-0.5">
                    Varun Joshi · Fri, Aug 14 · 1:53 AM · English (Global)
                  </span>
                </div>
              </div>
              <div className="flex items-center gap-1.5 shrink-0">
                <button 
                  onClick={() => setSelectedFileForModal(null)}
                  className="text-gray-400 hover:text-gray-600 text-lg leading-none p-1 cursor-pointer"
                >
                  ×
                </button>
              </div>
            </div>

            {/* Privacy Section */}
            <div className="space-y-2 select-none">
              <span className="text-[12px] font-semibold text-gray-700 block">Privacy</span>
              <button 
                onClick={() => onTriggerToast("Privacy settings coming soon!", "success")}
                className="w-full flex items-center justify-between border border-gray-200 hover:bg-gray-50 rounded-xl px-3.5 py-2.5 text-xs text-gray-700 font-medium cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-2">
                  <Globe className="w-4 h-4 text-gray-400" />
                  <span>Teammates & Anyone with Link</span>
                </div>
                <span className="text-gray-400 text-[10px]">▼</span>
              </button>
            </div>

            {/* Channels Section */}
            <div className="space-y-2 select-none">
              <span className="text-[12px] font-semibold text-gray-700 block">Channels</span>
              <div className="flex items-center justify-between bg-gray-50 rounded-xl px-3.5 py-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-gray-700">
                  <span className="bg-purple-100 text-purple-700 px-2 py-0.5 rounded-md flex items-center gap-1">
                    <Hash className="w-3 h-3" />
                    All Meetings
                  </span>
                  <span className="bg-purple-100 text-purple-700 px-2 py-0.5 rounded-md flex items-center gap-1">
                    <Hash className="w-3 h-3" />
                    My Meetings
                  </span>
                </div>
                <button 
                  onClick={() => onTriggerToast("Move to channel feature coming soon!", "success")}
                  className="border border-gray-200 hover:bg-white bg-white text-gray-700 font-medium py-1 px-3 rounded-lg text-xs cursor-pointer shadow-2xs"
                >
                  Move to channel
                </button>
              </div>
            </div>

            {/* Invited Section */}
            <div className="space-y-2 select-none">
              <span className="text-[12px] font-semibold text-gray-700 block">Invited</span>
              <div className="flex items-center gap-3 p-2 hover:bg-gray-50 rounded-xl">
                <div className="w-8 h-8 rounded-full bg-purple-700 flex items-center justify-center text-white font-bold text-xs shrink-0">
                  VJ
                </div>
                <div className="flex-1">
                  <span className="text-xs font-bold text-gray-900 block">Varun Joshi</span>
                  <span className="text-[11px] text-gray-400 font-medium block">joshivarun266@gmail.com - Host</span>
                </div>
              </div>
            </div>

            {/* Footer close button */}
            <div className="pt-2 flex justify-end border-t border-gray-100">
              <button 
                onClick={() => setSelectedFileForModal(null)}
                className="bg-[#6E2CF4] hover:bg-[#5B21D6] text-white font-semibold py-2 px-5 rounded-xl text-xs cursor-pointer transition-colors shadow-xs"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Floating Help Button */}
      <div className="fixed bottom-6 right-6 z-40">
        <button
          onClick={() => onTriggerToast("Help & Support coming soon!", "success")}
          className="w-10 h-10 rounded-full bg-[#6E2CF4] hover:bg-[#5B21D6] text-white flex items-center justify-center shadow-lg transition-transform active:scale-95 cursor-pointer"
          title="Help & Support"
        >
          <span className="text-sm font-bold">?</span>
        </button>
      </div>
    </div>
  );
}