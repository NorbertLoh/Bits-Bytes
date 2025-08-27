import React, { useState, useCallback } from 'react';
import FileUpload from './FileUpload';
import Spinner from './Spinner';

const BulkProcessor: React.FC = () => {
  // State for PDF to Excel Converter
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [isConvertingPdf, setIsConvertingPdf] = useState(false);
  const [convertedExcelUrl, setConvertedExcelUrl] = useState<string | null>(null);
  const [pdfError, setPdfError] = useState<string | null>(null);

  // State for Excel Feature Analyzer
  const [excelFile, setExcelFile] = useState<File | null>(null);
  const [isProcessingExcel, setIsProcessingExcel] = useState(false);
  const [processedExcelUrl, setProcessedExcelUrl] = useState<string | null>(null);
  const [excelError, setExcelError] = useState<string | null>(null);

  // --- Handlers for PDF Converter ---
  const handlePdfSelect = useCallback((file: File) => {
    setPdfFile(file);
    setPdfError(null);
    if (convertedExcelUrl) {
      URL.revokeObjectURL(convertedExcelUrl);
      setConvertedExcelUrl(null);
    }
  }, [convertedExcelUrl]);

  const handlePdfConversion = async () => {
    // if (!pdfFile) {
    //   setPdfError('Please select a PDF file first.');
    //   return;
    // }
    // setIsConvertingPdf(true);
    // setPdfError(null);
    // try {
    //   const excelBlob = await convertPdfToExcel(pdfFile);
    //   const url = URL.createObjectURL(excelBlob);
    //   setConvertedExcelUrl(url);
    // } catch (err) {
    //   setPdfError(err instanceof Error ? err.message : 'PDF conversion failed.');
    // } finally {
    //   setIsConvertingPdf(false);
    // }
  };
  
  const resetPdfConverter = () => {
    setPdfFile(null);
    if (convertedExcelUrl) {
      URL.revokeObjectURL(convertedExcelUrl);
    }
    setConvertedExcelUrl(null);
    setPdfError(null);
  };

  // --- Handlers for Excel Analyzer ---
  const handleExcelSelect = useCallback((file: File) => {
    setExcelFile(file);
    setExcelError(null);
    if (processedExcelUrl) {
      URL.revokeObjectURL(processedExcelUrl);
      setProcessedExcelUrl(null);
    }
  }, [processedExcelUrl]);

  const handleExcelProcessing = async () => {
//     if (!excelFile) {
//       setExcelError('Please upload an Excel file.');
//       return;
//     }
//     setIsProcessingExcel(true);
//     setExcelError(null);
//     try {
//       const processedBlob = await processExcelFile(excelFile);
//       const url = URL.createObjectURL(processedBlob);
//       setProcessedExcelUrl(url);
//     } catch (err)
//  {
//       setExcelError(err instanceof Error ? err.message : 'Excel processing failed.');
//     } finally {
//       setIsProcessingExcel(false);
//     }
  };

  const resetExcelAnalyzer = () => {
    setExcelFile(null);
    if (processedExcelUrl) {
      URL.revokeObjectURL(processedExcelUrl);
    }
    setProcessedExcelUrl(null);
    setExcelError(null);
  };

  const actionButtonClasses = "mt-4 w-full flex justify-center items-center bg-cyan-400 text-black font-bold py-2 px-4 rounded-md hover:bg-cyan-500 disabled:bg-slate-700 disabled:text-slate-400 disabled:cursor-not-allowed transition-colors";

  return (
    <div className="bg-slate-900 p-6 sm:p-8 rounded-xl border border-slate-700 max-w-3xl mx-auto">
      <h2 className="text-xl font-semibold text-slate-100">Batch Feature Processing Tools</h2>

      {/* Section 1: PDF to Excel Converter */}
      <div className="mt-6 border-t border-slate-700 pt-6">
        <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium text-slate-100">1. PDF to Excel Converter</h3>
            <button onClick={resetPdfConverter} className="text-sm text-cyan-400 hover:underline disabled:text-slate-600 disabled:no-underline disabled:cursor-not-allowed" disabled={isConvertingPdf}>Reset</button>
        </div>
        <p className="mt-1 text-sm text-slate-400">
          Convert a PDF document with feature descriptions into an Excel file.
        </p>
        
        {!convertedExcelUrl && (
            <div className="mt-4">
                <FileUpload acceptedFileTypes=".pdf" onFileSelect={handlePdfSelect} />
                {pdfFile && <p className="mt-2 text-sm text-center text-slate-400">Selected: {pdfFile.name}</p>}
                <button onClick={handlePdfConversion} disabled={!pdfFile || isConvertingPdf} className={actionButtonClasses}>
                    {isConvertingPdf ? <Spinner /> : 'Convert to Excel'}
                </button>
            </div>
        )}
        
        {pdfError && <div className="mt-4 text-red-300 bg-red-900/50 p-3 rounded-md border border-red-500/50">{pdfError}</div>}
        
        {convertedExcelUrl && (
            <div className="mt-4 text-center p-4 bg-green-900/40 rounded-lg border border-green-500/30">
                <h4 className="font-semibold text-green-300">Conversion Successful!</h4>
                <a href={convertedExcelUrl} download={`${pdfFile?.name.replace(/\.[^/.]+$/, "") || 'converted'}.xlsx`} className="mt-2 inline-block w-full bg-green-500 text-white font-bold py-2 px-4 rounded-md hover:bg-green-600">
                    Download Excel File
                </a>
            </div>
        )}
      </div>
      
      {/* Section 2: Excel Feature Analyzer */}
      <div className="mt-8 border-t border-slate-700 pt-6">
        <div className="flex justify-between items-center">
            <h3 className="text-lg font-medium text-slate-100">2. Excel Feature Analyzer</h3>
            <button onClick={resetExcelAnalyzer} className="text-sm text-cyan-400 hover:underline disabled:text-slate-600 disabled:no-underline disabled:cursor-not-allowed" disabled={isProcessingExcel}>Reset</button>
        </div>
        <p className="mt-1 text-sm text-slate-400">
          Upload an Excel file (e.g., from the converter above) to analyze all feature descriptions in bulk.
        </p>
        
        {!processedExcelUrl && (
            <div className="mt-4">
                <FileUpload acceptedFileTypes=".xlsx, .xls" onFileSelect={handleExcelSelect} />
                {excelFile && <p className="mt-2 text-sm text-center text-slate-400">Selected: {excelFile.name}</p>}
                <button onClick={handleExcelProcessing} disabled={!excelFile || isProcessingExcel} className={actionButtonClasses}>
                    {isProcessingExcel ? <Spinner /> : 'Analyze Excel File'}
                </button>
            </div>
        )}

        {excelError && <div className="mt-4 text-red-300 bg-red-900/50 p-3 rounded-md border border-red-500/50">{excelError}</div>}
        
        {processedExcelUrl && (
            <div className="mt-4 text-center p-4 bg-green-900/40 rounded-lg border border-green-500/30">
                <h4 className="font-semibold text-green-300">Analysis Complete!</h4>
                <a href={processedExcelUrl} download={`processed_${excelFile?.name || 'features.xlsx'}`} className="mt-2 inline-block w-full bg-green-500 text-white font-bold py-2 px-4 rounded-md hover:bg-green-600">
                    Download Processed File
                </a>
            </div>
        )}
      </div>
    </div>
  );
};

export default BulkProcessor;