import Link from "next/link";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
      <main className="flex min-h-screen w-full max-w-4xl flex-col items-center justify-center py-16 px-8">
        <div className="flex flex-col items-center gap-8 text-center">
          <h1 className="text-4xl font-bold leading-tight tracking-tight text-gray-900 dark:text-white">
            Multi-Agent Content Pipeline
          </h1>
          <p className="max-w-2xl text-lg leading-8 text-gray-600 dark:text-gray-400">
            AI-powered content generation using a multi-agent workflow with research, 
            writing, fact-checking, and style polishing.
          </p>
        </div>
        
        <div className="mt-6 text-sm text-gray-500 dark:text-gray-400 text-center">
          <p>
            Live demo is password protected to avoid abuse of API credits. Ask the
            project owner for the demo password, then log in on the next page.
          </p>
        </div>

        <div className="mt-8 grid gap-6 md:grid-cols-2 w-full max-w-2xl">
          <Link
            href="/posts"
            className="flex flex-col h-48 items-center justify-center rounded-lg bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 p-6 transition-all hover:border-blue-500 dark:hover:border-blue-400 hover:shadow-lg"
          >
            <div className="text-4xl mb-4">📋</div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              View Posts
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
              Browse all generated blog posts and view their generation timelines
            </p>
          </Link>
          
          <Link
            href="/generate"
            className="flex flex-col h-48 items-center justify-center rounded-lg bg-white dark:bg-gray-800 border-2 border-gray-200 dark:border-gray-700 p-6 transition-all hover:border-blue-500 dark:hover:border-blue-400 hover:shadow-lg"
          >
            <div className="text-4xl mb-4">🚀</div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              Generate Content
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 text-center">
              Create a new blog post from a Product Requirements Document
            </p>
          </Link>
        </div>

        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            API Endpoint: <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">POST /api/generate</code>
          </p>
        </div>
      </main>
    </div>
  );
}
