// Format date to readable string
export const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
};

// Return tailwind color class based on status
export const getStatusColor = (status) => {
  switch (status?.toLowerCase()) {
    case 'pending':   return 'text-amber-400 bg-amber-400/10 border-amber-400/30';
    case 'cleaned':   return 'text-emerald-400 bg-emerald-400/10 border-emerald-400/30';
    case 'in_progress': return 'text-cyan-400 bg-cyan-400/10 border-cyan-400/30';
    default:          return 'text-slate-400 bg-slate-400/10 border-slate-400/30';
  }
};

// Truncate long text
export const truncate = (text, length = 40) =>
  text?.length > length ? text.slice(0, length) + '...' : text;

// ─── Dummy Data ───────────────────────────────────────────

export const DUMMY_REPORTS = [
  { id: '1', image: 'https://picsum.photos/seed/waste1/300/200', location: '12.9716° N, 77.5946° E', description: 'Overflowing bin near cafeteria', status: 'pending', createdAt: '2026-04-10T09:00:00Z', reporter: 'Aryan Mehta' },
  { id: '2', image: 'https://picsum.photos/seed/waste2/300/200', location: '12.9720° N, 77.5950° E', description: 'Plastic waste near science block', status: 'cleaned', createdAt: '2026-04-11T10:30:00Z', reporter: 'Priya Sharma' },
  { id: '3', image: 'https://picsum.photos/seed/waste3/300/200', location: '12.9710° N, 77.5940° E', description: 'Bio-waste in hostel corridor', status: 'in_progress', createdAt: '2026-04-12T08:15:00Z', reporter: 'Ravi Kumar' },
  { id: '4', image: 'https://picsum.photos/seed/waste4/300/200', location: '12.9730° N, 77.5960° E', description: 'Littering near sports ground', status: 'pending', createdAt: '2026-04-13T11:00:00Z', reporter: 'Sneha Patel' },
  { id: '5', image: 'https://picsum.photos/seed/waste5/300/200', location: '12.9705° N, 77.5935° E', description: 'Broken glass on walkway', status: 'cleaned', createdAt: '2026-04-14T07:45:00Z', reporter: 'Karan Singh' },
];

export const DUMMY_LEADERBOARD = [
  { id: '1', name: 'Aryan Mehta',  email: 'aryan@campus.edu',  points: 450, reports: 18, avatar: 'AM' },
  { id: '2', name: 'Priya Sharma', email: 'priya@campus.edu',  points: 380, reports: 15, avatar: 'PS' },
  { id: '3', name: 'Ravi Kumar',   email: 'ravi@campus.edu',   points: 320, reports: 12, avatar: 'RK' },
  { id: '4', name: 'Sneha Patel',  email: 'sneha@campus.edu',  points: 290, reports: 11, avatar: 'SP' },
  { id: '5', name: 'Karan Singh',  email: 'karan@campus.edu',  points: 250, reports: 10, avatar: 'KS' },
  { id: '6', name: 'Divya Nair',   email: 'divya@campus.edu',  points: 210, reports: 8,  avatar: 'DN' },
  { id: '7', name: 'Amit Verma',   email: 'amit@campus.edu',   points: 180, reports: 7,  avatar: 'AV' },
  { id: '8', name: 'Rohit Joshi',  email: 'rohit@campus.edu',  points: 150, reports: 6,  avatar: 'RJ' },
];

export const DUMMY_MAP_MARKERS = [
  { id: 1, lat: 12.9716, lng: 77.5946, title: 'Cafeteria Bin', status: 'pending',    description: 'Overflowing bin near cafeteria' },
  { id: 2, lat: 12.9720, lng: 77.5950, title: 'Science Block', status: 'cleaned',    description: 'Plastic waste near science block' },
  { id: 3, lat: 12.9710, lng: 77.5940, title: 'Hostel Block',  status: 'in_progress',description: 'Bio-waste in hostel corridor' },
  { id: 4, lat: 12.9730, lng: 77.5960, title: 'Sports Ground', status: 'pending',    description: 'Littering near sports ground' },
  { id: 5, lat: 12.9705, lng: 77.5935, title: 'Main Walkway',  status: 'cleaned',    description: 'Broken glass on walkway' },
];
