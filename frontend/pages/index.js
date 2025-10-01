import { useState, useRef } from 'react';

// SVG Icon Components for better UI
const UploadIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
    </svg>
);

const DownloadIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
);

const Spinner = () => (
    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
);

export default function Home() {
    const [file, setFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [downloadUrl, setDownloadUrl] = useState(null);
    const fileInputRef = useRef(null);

    // Handles file selection from the input
    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile && selectedFile.type === 'application/pdf') {
            setFile(selectedFile);
            setError(null);
            setDownloadUrl(null); // Reset download link on new file selection
        } else {
            setFile(null);
            setError('Please select a valid PDF file.');
        }
    };

    // Handles drag and drop
    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        e.target.classList.remove('border-indigo-500');
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile && droppedFile.type === 'application/pdf') {
            setFile(droppedFile);
            setError(null);
            setDownloadUrl(null);
        } else {
            setFile(null);
            setError('Please drop a valid PDF file.');
        }
    };

    // Form submission handler
    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!file) {
            setError('Please select a resume to enhance.');
            return;
        }

        setIsLoading(true);
        setError(null);
        setDownloadUrl(null);

        const formData = new FormData();
        formData.append('resume', file);

        try {
            const response = await fetch('/api/enhance', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.details || `An error occurred: ${response.statusText}`);
            }

            // Create a downloadable link for the returned PDF blob
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            setDownloadUrl(url);

        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const resetState = () => {
        setFile(null);
        setIsLoading(false);
        setError(null);
        setDownloadUrl(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    };

    return (
        <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50 font-sans p-4">
            <div className="w-full max-w-2xl">
                <header className="text-center mb-8">
                    <h1 className="text-4xl md:text-5xl font-bold text-gray-800">Intelligent Resume Enhancer</h1>
                    <p className="text-gray-600 mt-2">Optimize your resume for ATS with AI. Powered by LangGraph & Groq.</p>
                </header>

                <main className="bg-white rounded-xl shadow-lg p-6 md:p-10 w-full">
                    {!downloadUrl ? (
                        <form onSubmit={handleSubmit}>
                            <div
                                className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer transition-all duration-300 hover:border-indigo-500 bg-gray-50"
                                onDragOver={(e) => { e.preventDefault(); e.target.classList.add('border-indigo-500'); }}
                                onDragLeave={(e) => { e.preventDefault(); e.target.classList.remove('border-indigo-500'); }}
                                onDrop={handleDrop}
                                onClick={() => fileInputRef.current.click()}
                            >
                                <input
                                    type="file"
                                    accept="application/pdf"
                                    onChange={handleFileChange}
                                    className="hidden"
                                    ref={fileInputRef}
                                />
                                {isLoading ? (
                                    <div className="flex flex-col items-center justify-center">
                                        <Spinner />
                                        <p className="mt-4 text-gray-600">Enhancing your resume... this may take a moment.</p>
                                    </div>
                                ) : (
                                    <>
                                        <div className="flex justify-center mb-4">
                                            <UploadIcon />
                                        </div>
                                        {file ? (
                                            <p className="text-gray-700 font-medium">{file.name}</p>
                                        ) : (
                                            <p className="text-gray-500">
                                                <span className="font-semibold text-indigo-600">Click to upload</span> or drag and drop your PDF resume here.
                                            </p>
                                        )}
                                    </>
                                )}
                            </div>
                            
                            {error && <p className="text-red-500 mt-4 text-center">{error}</p>}
                            
                            <div className="mt-6 text-center">
                                <button
                                    type="submit"
                                    disabled={!file || isLoading}
                                    className="w-full sm:w-auto px-8 py-3 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 disabled:bg-indigo-300 disabled:cursor-not-allowed transition-all duration-300"
                                >
                                    Enhance Resume
                                </button>
                            </div>
                        </form>
                    ) : (
                        <div className="text-center">
                            <h2 className="text-2xl font-semibold text-gray-800 mb-4">Your Resume is Ready!</h2>
                            <p className="text-gray-600 mb-6">Your enhanced, ATS-friendly resume has been generated.</p>
                            <a
                                href={downloadUrl}
                                download="enhanced_resume.pdf"
                                className="inline-flex items-center justify-center px-8 py-3 bg-green-600 text-white font-semibold rounded-lg shadow-md hover:bg-green-700 transition-all duration-300"
                            >
                                <DownloadIcon />
                                Download Now
                            </a>
                            <button
                                onClick={resetState}
                                className="mt-4 w-full sm:w-auto text-indigo-600 font-semibold hover:underline"
                            >
                                Enhance another resume
                            </button>
                        </div>
                    )}
                </main>

                <footer className="text-center mt-8 text-gray-500 text-sm">
                    <p>&copy; {new Date().getFullYear()} Resume Enhancer. All rights reserved.</p>
                </footer>
            </div>
        </div>
    );
}
