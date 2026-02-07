# Test Writer Frontend

A Next.js frontend for the Test Writer document upload system.

## Features

- 📁 **Drag & Drop File Upload** - Intuitive file upload interface
- 📊 **File Management** - View, download, and delete uploaded files
- 🎨 **Modern UI** - Clean, responsive design with Tailwind CSS
- ⚡ **Real-time Progress** - Upload progress tracking
- 🔍 **File Information** - Display file size, type, and upload date

## Getting Started

### Prerequisites

- Node.js 18+ installed
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Usage

### Upload Files

1. **Drag & Drop**: Drag files directly onto the upload area
2. **Click to Browse**: Click "Browse Files" to select files
3. **Supported Formats**: PDF, DOC, DOCX, TXT, JPG, PNG
4. **File Size Limit**: Maximum 10MB per file

### Manage Files

- **Download**: Click the download button to save files
- **Delete**: Remove files with the delete button
- **Refresh**: Update the file list with the refresh button

## API Integration

The frontend connects to the backend API at `http://localhost:8000/api/v1`:

- `POST /files/upload` - Upload files
- `GET /files/` - List all files
- `GET /files/{id}/download` - Download files
- `DELETE /files/{id}` - Delete files

## Project Structure

```
frontend/
├── app/
│   ├── page.tsx              # Main upload interface
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
├── package.json              # Dependencies
├── tailwind.config.js        # Tailwind configuration
├── next.config.js            # Next.js configuration
└── README.md                 # This file
```

## Technologies Used

- **Next.js 14** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Adding Features

The main component is in `app/page.tsx`. Key functions:
- `handleFileUpload()` - File upload logic
- `loadFiles()` - Fetch file list
- `downloadFile()` - Download files
- `deleteFile()` - Delete files

## Production

Build the application:
```bash
npm run build
npm start
```

The app will be available at `http://localhost:3000`.
