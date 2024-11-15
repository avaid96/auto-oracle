'use client'

import * as React from 'react'
import { useState, useEffect } from 'react'
import { Upload, FileText, Send, Download } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Progress } from '@/components/ui/progress'
import Image from 'next/image'

// Mock API calls
// const findQuestions = async (file: File) => {
//   await new Promise(resolve => setTimeout(resolve, 2000))
//   return [
//     'Is the system SOC2 compliant?',
//     'Can users delete their data?'
//   ]
// }

const findQuestions = async (file: File) => {
  try {

    // Create FormData object
    const formData = new FormData();
    formData.append('file', file);

    // First, upload the file to get its path
    const uploadResponse = await fetch('http://localhost:5001/upload', {
      method: 'POST',
      body: formData
    });
    
    if (!uploadResponse.ok) {
      throw new Error(`Upload failed! status: ${uploadResponse.status}`);
    }
    const { filePath } = await uploadResponse.json();


    console.log("Hello, World!");

    const response = await fetch('http://localhost:5001/parse', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        doc_path: filePath
      })
    });
    
    console.log("Received response");
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }

    return data.questions;

  } catch (error) {
    console.error('Error in findQuestions:', error);
    throw error;
  }
}

const getAnswer = async (question: string, chatbotUrl: string) => {
  try {
    const response = await fetch('http://localhost:5001/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question: question,
        chatbot_link: chatbotUrl
      })
    });

    if (!response.ok) {
      throw new Error(`Answer request failed! status: ${response.status}`);
    }

    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error);
    }

    return data.answer;

  } catch (error) {
    console.error('Error in getAnswer:', error);
    throw error;
  }
}

type Step = 'upload' | 'processing' | 'review'
type Status = 'waiting' | 'processing' | 'done'

export function AutoOracle() {
  const [step, setStep] = useState<Step>('upload')
  const [file, setFile] = useState<File | null>(null)
  const [chatbotUrl, setChatbotUrl] = useState('')
  const [questions, setQuestions] = useState<string[]>([])
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [processStatus, setProcessStatus] = useState({
    findQuestions: 'waiting' as Status,
    answerQuestions: 'waiting' as Status,
    compileResults: 'waiting' as Status
  })
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [fileUrl, setFileUrl] = useState<string>('');
  const [isEditing, setIsEditing] = useState<Record<string, boolean>>({});
  const [followUpQuestion, setFollowUpQuestion] = useState('');
  const [isLoadingAnswer, setIsLoadingAnswer] = useState(false);
  const [pendingQA, setPendingQA] = useState<{ question: string; answer: string } | null>(null);
  const [isGeneratingDoc, setIsGeneratingDoc] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      // Create and set object URL for the file
      const url = URL.createObjectURL(selectedFile);
      setFileUrl(url);
    }
  }

  useEffect(() => {
    return () => {
      // Cleanup object URL when component unmounts
      if (fileUrl) {
        URL.revokeObjectURL(fileUrl);
      }
    };
  }, [fileUrl]);

  const startProcessing = async () => {
    if (!file) return

    setStep('processing')
    
    // Find questions
    setProcessStatus(prev => ({ ...prev, findQuestions: 'processing' }))
    const foundQuestions = await findQuestions(file)
    setQuestions(foundQuestions)
    setProcessStatus(prev => ({ ...prev, findQuestions: 'done', answerQuestions: 'processing' }))

    // Get answers
    const newAnswers: Record<string, string> = {}
    
    // First, start all API calls without delay
    const answerPromises = foundQuestions.map((question: string) => 
      getAnswer(question, chatbotUrl)
    );

    // Then, update progress with delay while answers are being fetched
    const updateProgressWithDelay = async () => {
      for (let i = 0; i < foundQuestions.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 5000));
        setCurrentQuestion(i + 1);
      }
    };

    // Run both processes
    const [answers] = await Promise.all([
      Promise.all(answerPromises),
      updateProgressWithDelay()
    ]);

    // Format results after all promises complete
    const results = foundQuestions.map((question: string, index: number) => ({
      question,
      answer: answers[index]
    }));

    // Combine results into newAnswers object
    results.forEach(({ question, answer }: { question: string, answer: string }) => {
      newAnswers[question] = answer
    })
    setAnswers(newAnswers)
    setProcessStatus(prev => ({ ...prev, answerQuestions: 'done', compileResults: 'done' }))

    // Move to review
    setStep('review')
  }

  const exportAnswers = () => {
    const csv = questions.map(q => `"${q}","${answers[q]}"`).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'answers.csv'
    a.click()
  }

  const handleAnswerChange = (question: string, newAnswer: string) => {
    setAnswers(prev => ({
      ...prev,
      [question]: newAnswer
    }));
  };

  const handleFollowUpQuestion = async () => {
    if (!followUpQuestion.trim()) return;
    
    setIsLoadingAnswer(true);
    try {
      const answer = await getAnswer(followUpQuestion, chatbotUrl);
      setPendingQA({ question: followUpQuestion, answer });
      setFollowUpQuestion('');
    } catch (error) {
      console.error('Error getting follow-up answer:', error);
    } finally {
      setIsLoadingAnswer(false);
    }
  };

  const handleAddToList = () => {
    if (pendingQA) {
      setQuestions(prev => [...prev, pendingQA.question]);
      setAnswers(prev => ({
        ...prev,
        [pendingQA.question]: pendingQA.answer
      }));
      setPendingQA(null);
    }
  };

  const handleGenerateDoc = async () => {
    if (!file) return;
    
    try {
      setIsGeneratingDoc(true);
      const response = await fetch('http://localhost:5001/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          documentName: file.name,
          qaArray: questions.map(question => ({
            question,
            answer: answers[question]
          }))
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate document');
      }
      
      // Get the blob from the response
      const blob = await response.blob();
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'generated-document.docx';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
      
    } catch (error) {
      console.error('Error generating document:', error);
    } finally {
      setIsGeneratingDoc(false);
    }
  };

  // const HARDCODED_DOC_URL = "https://docs.google.com/document/d/1VGtDrDYVpAmLwEG1vJvwOmHKCWaOBrFxOXZtQkxBj4Y/edit"; // Replace with your Google Doc URL
  const DROPBOX_URL = "https://www.dropbox.com/scl/fi/pdtiskoj2efhjzwv585eo/Sample-RFP.docx?rlkey=s9wu2cy6dbn2ucu3lri7ka73r&e=1&st=0gyoqc8i&dl=0"; // Replace with your Dropbox link

  // Helper function to convert Dropbox link to preview link
  const getDropboxPreviewUrl = (url: string) => {
    // Convert dropbox share link to direct download link
    return url.replace('www.dropbox.com', 'dl.dropboxusercontent.com').replace('?dl=0', '');
  };

  // At the top of your component, add this helper function
  const getGoogleDocsViewerUrl = (fileUrl: string) => {
    // return `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(fileUrl)}`;
    return `https://view.officeapps.live.com/op/embed.aspx?src=${encodeURIComponent(fileUrl)}`;
  };

  if (step === 'upload') {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="w-full max-w-2xl">
          <CardContent className="p-8">
            {/* Header Section */}
            <div className="flex items-start gap-4 mb-8">
              <div className="mt-1">
                <Image 
                  src="/images/logo.png"
                  alt="AI Hub Logo"
                  width={120}
                  height={40}
                  className="object-contain"
                />
              </div>
              <div>
                <h1 className="text-3xl font-semibold">Auto Oracle</h1>
                <p className="text-muted-foreground mt-1">
                  Instantly answer any questionnaire or create a memo
                </p>
              </div>
            </div>
            
            {/* Upload Section */}
            <div className="space-y-8">
              <div className="space-y-4">
                <div className="space-y-2">
                  <h2 className="text-xl font-medium">Step 1: Upload your questionnaire</h2>
                  <p className="text-sm text-muted-foreground">
                    Upload your document in PDF, DOC, or DOCX format
                  </p>
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <Input
                        type="file"
                        onChange={handleFileChange}
                        accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        className="w-full file:mr-4 file:py-2 file:px-4 
                                  file:rounded-full file:border-0 
                                  file:text-sm file:font-semibold 
                                  file:bg-primary file:text-primary-foreground
                                  hover:file:bg-primary/90"
                      />
                    </div>
                    <Upload className="h-5 w-5 text-muted-foreground shrink-0" />
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    Supported formats: PDF (.pdf), Word Document (.doc, .docx)
                  </p>
                </div>

                <div className="space-y-4">
                  <div className="space-y-2">
                    <h2 className="text-xl font-medium">Step 2: Select a chatbot</h2>
                    <p className="text-sm text-muted-foreground">
                      Enter the URL of your AI Hub chatbot
                    </p>
                  </div>
                  <Input
                    type="url"
                    placeholder="Enter an AI Hub chatbot URL"
                    value={chatbotUrl}
                    onChange={(e) => setChatbotUrl(e.target.value)}
                    className="h-12"
                  />
                </div>

                <Button
                  onClick={startProcessing}
                  disabled={!file || !chatbotUrl}
                  className="w-full h-12 text-lg mt-4"
                >
                  <Upload className="mr-2 h-5 w-5" />
                  Start Processing
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (step === 'processing') {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <Card className="w-full max-w-2xl">
          <CardContent className="p-6 space-y-6">
            <div className="flex items-center gap-4 mb-6">
              <Image 
                src="/images/logo.png"
                alt="AI Hub Logo"
                width={120}
                height={40}
                className="object-contain"
              />
              <h1 className="text-2xl font-bold">Auto Oracle</h1>
            </div>
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Finding Questions</span>
                  <span className={processStatus.findQuestions === 'done' ? 'text-green-500' : 'text-muted-foreground'}>
                    {processStatus.findQuestions === 'done' ? 'Done' : 'Processing...'}
                  </span>
                </div>
                <Progress value={processStatus.findQuestions === 'done' ? 100 : 60} />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Answering Questions</span>
                  <span className="text-muted-foreground">
                    {processStatus.answerQuestions === 'processing' ? `${currentQuestion}/${questions.length}` : ''}
                  </span>
                </div>
                <Progress 
                  value={processStatus.answerQuestions === 'done' ? 100 : (currentQuestion / questions.length) * 100} 
                />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Compiling Results</span>
                  <span className={processStatus.compileResults === 'done' ? 'text-green-500' : 'text-muted-foreground'}>
                    {processStatus.compileResults === 'done' ? 'Done' : 'Waiting...'}
                  </span>
                </div>
                <Progress value={processStatus.compileResults === 'done' ? 100 : 0} />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="h-screen p-6 bg-background">
      <Card className="w-full h-full">
        <CardContent className="p-6 h-full flex flex-col">
          {/* Fixed Header */}
          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-4">
              <Image 
                src="/images/logo.png"
                alt="AI Hub Logo"
                width={120}
                height={40}
                className="object-contain"
              />
              <h1 className="text-2xl font-bold">Auto Oracle</h1>
            </div>
            <div className="flex items-center gap-4">
              <Button onClick={exportAnswers} variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Export Answers
              </Button>
              <Button 
                onClick={handleGenerateDoc} 
                variant="outline"
                disabled={isGeneratingDoc}
              >
                <FileText className="h-4 w-4 mr-2" />
                {isGeneratingDoc ? 'Generating...' : 'Generate DOCX'}
              </Button>
            </div>
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-2 gap-6 flex-1">
            {/* Document Preview - Fixed */}
            <Card className="col-span-1">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2 mb-4">
                  <FileText className="h-5 w-5" />
                  <h2 className="text-lg font-medium">Document Preview</h2>
                </div>
                {file ? (
                  file.type === 'application/pdf' ? (
                    <object
                      data={fileUrl}
                      type="application/pdf"
                      className="w-full h-[600px] rounded-lg"
                    >
                      <p>Unable to display PDF. <a href={fileUrl} target="_blank" rel="noopener noreferrer">Download instead</a></p>
                    </object>
                  ) : file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || 
                       file.type === 'application/msword' ? (
                        <iframe
                          src={getGoogleDocsViewerUrl(getDropboxPreviewUrl(DROPBOX_URL))}
                          className="w-full h-[800px] rounded-lg border-0"
                        />
                      ) : (
                        <div className="h-[600px] bg-muted rounded-lg flex items-center justify-center flex-col p-4">
                          <FileText className="h-12 w-12 text-muted-foreground mb-2" />
                          <p className="text-center text-sm text-muted-foreground">
                            Preview not available for {file.type} files.
                            <br />
                            <a href={fileUrl} download className="text-primary hover:underline">
                              Download file
                            </a>
                          </p>
                        </div>
                      )
                ) : (
                  <div className="h-[600px] bg-muted rounded-lg flex items-center justify-center">
                    <FileText className="h-12 w-12 text-muted-foreground" />
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Q&A Section - Scrollable */}
            <div className="col-span-1 flex flex-col h-[800px]">
              <div className="bg-background sticky top-0 z-10 p-4 border-b">
                <h2 className="text-lg font-medium">Questions & Answers</h2>
              </div>
              
              <div className="flex-1 overflow-y-auto">
                <div className="space-y-4 p-4 pb-16">
                  {/* Show pending Q&A if exists */}
                  {pendingQA && (
                    <div className="bg-muted/50 rounded-lg p-4 border-2 border-primary">
                      <div className="font-semibold text-primary mb-2 text-base border-l-4 border-primary pl-3">
                        {pendingQA.question}
                      </div>
                      <div className="text-sm text-muted-foreground font-normal pl-3 mb-4">
                        {pendingQA.answer}
                      </div>
                      <Button 
                        onClick={handleAddToList}
                        className="w-full"
                      >
                        Add to List
                      </Button>
                    </div>
                  )}
                  
                  {/* Existing questions */}
                  {questions.map((question) => (
                    <div key={question} className="bg-muted rounded-lg p-4">
                      <div className="font-semibold text-primary mb-2 text-base border-l-4 border-primary pl-3">
                        {question}
                      </div>
                      <div 
                        className="text-sm text-muted-foreground font-normal pl-3 relative group"
                        onDoubleClick={() => setIsEditing(prev => ({ ...prev, [question]: true }))}
                      >
                        {isEditing[question] ? (
                          <textarea
                            value={answers[question]}
                            onChange={(e) => handleAnswerChange(question, e.target.value)}
                            onBlur={() => setIsEditing(prev => ({ ...prev, [question]: false }))}
                            className="w-full min-h-[100px] p-2 rounded border border-input bg-background"
                            autoFocus
                          />
                        ) : (
                          <div className="group-hover:bg-background/50 p-2 rounded">
                            {answers[question]}
                            <span className="hidden group-hover:inline text-xs text-muted-foreground ml-2">
                              (Double click to edit)
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="sticky bottom-0 bg-background p-4 border-t">
                <div className="flex space-x-2">
                  <Input 
                    placeholder="Ask a follow-up question..." 
                    className="flex-1"
                    value={followUpQuestion}
                    onChange={(e) => setFollowUpQuestion(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        handleFollowUpQuestion();
                      }
                    }}
                    disabled={isLoadingAnswer}
                  />
                  <Button 
                    size="icon"
                    onClick={handleFollowUpQuestion}
                    disabled={!followUpQuestion.trim() || isLoadingAnswer}
                  >
                    {isLoadingAnswer ? (
                      <span className="animate-spin">⏳</span>
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}