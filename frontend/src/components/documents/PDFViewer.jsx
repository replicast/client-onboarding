import React, { useRef } from 'react';
import { Worker, Viewer } from '@react-pdf-viewer/core';
import { defaultLayoutPlugin } from '@react-pdf-viewer/default-layout';
import { searchPlugin } from '@react-pdf-viewer/search';

import '@react-pdf-viewer/core/lib/styles/index.css';
import '@react-pdf-viewer/default-layout/lib/styles/index.css';
import '@react-pdf-viewer/search/lib/styles/index.css';

function PDFViewer({ url, initialPage, initialSearch }) {
  const page = initialPage || 1;
  const search = initialSearch || '';

  const searchPluginRef = useRef(searchPlugin());
  const defaultLayoutPluginRef = useRef(defaultLayoutPlugin());
  const hasSearched = useRef(false);

  const searchPluginInstance = searchPluginRef.current;
  const defaultLayoutPluginInstance = defaultLayoutPluginRef.current;

  const handleDocumentLoad = () => {
    if (search && !hasSearched.current) {
      hasSearched.current = true;
      setTimeout(() => {
        searchPluginInstance.highlight([search])
          .then((matches) => {
            if (matches && matches.length > 0) {
              searchPluginInstance.jumpToMatch(0);
            }
          })
          .catch((err) => console.error('Search error:', err));
      }, 500);
    }
  };

  return (
    <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.11.174/build/pdf.worker.min.js">
      <div style={{ height: '100%', width: '100%' }}>
        <Viewer
          fileUrl={url}
          plugins={[defaultLayoutPluginInstance, searchPluginInstance]}
          initialPage={page - 1}
          defaultScale={1}
          onDocumentLoad={handleDocumentLoad}
        />
      </div>
    </Worker>
  );
}

export default PDFViewer;
