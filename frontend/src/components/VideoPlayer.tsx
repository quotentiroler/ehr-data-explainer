interface VideoPlayerProps {
  videoUrl: string
}

export default function VideoPlayer({ videoUrl }: VideoPlayerProps) {
  // Build full URL if it's a relative path
  const fullUrl = videoUrl.startsWith('http') ? videoUrl : videoUrl

  return (
    <div className="bg-white rounded-xl shadow-sm overflow-hidden">
      <div className="bg-gradient-to-r from-purple-500 to-purple-600 px-4 py-2">
        <h3 className="text-white font-medium flex items-center gap-2">
          <span>🎬</span> Your Health Explained
        </h3>
      </div>
      
      <div className="aspect-video bg-slate-900 relative">
        <video
          controls
          autoPlay
          loop
          muted
          playsInline
          className="w-full h-full object-contain"
          src={fullUrl}
        >
          <source src={fullUrl} type="video/mp4" />
          Your browser does not support video playback.
        </video>
        
        {/* Fallback loading state */}
        <div className="absolute inset-0 flex items-center justify-center bg-slate-900/50 opacity-0 hover:opacity-0 transition-opacity pointer-events-none">
          <div className="text-white text-center">
            <span className="text-4xl animate-pulse">🎥</span>
            <p className="text-sm mt-2">Loading video...</p>
          </div>
        </div>
      </div>
      
      <div className="px-4 py-2 bg-slate-50 text-xs text-slate-500 flex items-center justify-between">
        <span>Generated with Wan 2.2</span>
        <span className="text-slate-400">Educational content</span>
      </div>
    </div>
  )
}
