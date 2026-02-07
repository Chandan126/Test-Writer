import './globals.css'

export const metadata = {
  title: 'Test Writer - File Upload',
  description: 'Upload and manage your documents',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
