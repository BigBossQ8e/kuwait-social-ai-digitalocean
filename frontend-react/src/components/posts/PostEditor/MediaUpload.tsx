// Media upload component with drag and drop support

import React, { useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  useTheme,
  alpha,
} from '@mui/material';
import Grid from '@mui/material/Grid';
import {
  CloudUpload,
  Close,
  Image as ImageIcon,
  VideoLibrary,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { useAppSelector } from '../../../store';
import { selectLanguage } from '../../../store/slices/uiSlice';
import { VALIDATION } from '../../../utils/constants';

interface MediaFile {
  id: string | number;
  file?: File;
  url: string;
  type: 'image' | 'video';
}

interface MediaUploadProps {
  files: MediaFile[];
  onUpload: (files: File[]) => void;
  onRemove: (fileId: string | number) => void;
  maxFiles?: number;
  maxSize?: number;
  accept?: Record<string, string[]>;
}

export const MediaUpload: React.FC<MediaUploadProps> = ({
  files,
  onUpload,
  onRemove,
  maxFiles = 10,
  maxSize = VALIDATION.FILE_SIZE_LIMIT,
  accept = {
    'image/*': VALIDATION.SUPPORTED_IMAGE_TYPES,
    'video/*': VALIDATION.SUPPORTED_VIDEO_TYPES,
  },
}) => {
  const theme = useTheme();
  const language = useAppSelector(selectLanguage);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const remainingSlots = maxFiles - files.length;
    const filesToUpload = acceptedFiles.slice(0, remainingSlots);
    
    if (filesToUpload.length > 0) {
      onUpload(filesToUpload);
    }
  }, [files.length, maxFiles, onUpload]);

  const { getRootProps, getInputProps, isDragActive, isDragAccept, isDragReject } = useDropzone({
    onDrop,
    accept,
    maxSize,
    maxFiles: maxFiles - files.length,
    disabled: files.length >= maxFiles,
  });

  const getDropzoneStyle = () => {
    const baseStyle = {
      borderColor: theme.palette.divider,
      backgroundColor: theme.palette.background.paper,
      cursor: files.length >= maxFiles ? 'not-allowed' : 'pointer',
    };

    if (isDragAccept) {
      return {
        ...baseStyle,
        borderColor: theme.palette.success.main,
        backgroundColor: alpha(theme.palette.success.main, 0.05),
      };
    }

    if (isDragReject) {
      return {
        ...baseStyle,
        borderColor: theme.palette.error.main,
        backgroundColor: alpha(theme.palette.error.main, 0.05),
      };
    }

    if (isDragActive) {
      return {
        ...baseStyle,
        borderColor: theme.palette.primary.main,
        backgroundColor: alpha(theme.palette.primary.main, 0.05),
      };
    }

    return baseStyle;
  };

  return (
    <Box>
      {/* Uploaded Files Grid */}
      {files.length > 0 && (
        <Grid container spacing={2} sx={{ mb: 2 }}>
          {files.map((file) => (
            <Grid xs={6} sm={4} md={3} key={file.id}>
              <Paper
                sx={{
                  position: 'relative',
                  paddingTop: '100%',
                  overflow: 'hidden',
                  '&:hover .media-overlay': {
                    opacity: 1,
                  },
                }}
              >
                {file.type === 'image' ? (
                  <Box
                    component="img"
                    src={file.url}
                    alt="Upload"
                    sx={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                    }}
                  />
                ) : (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      height: '100%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      backgroundColor: theme.palette.grey[100],
                    }}
                  >
                    <VideoLibrary sx={{ fontSize: 48, color: theme.palette.grey[400] }} />
                  </Box>
                )}
                
                <Box
                  className="media-overlay"
                  sx={{
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    backgroundColor: 'rgba(0, 0, 0, 0.5)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    opacity: 0,
                    transition: 'opacity 0.3s',
                  }}
                >
                  <IconButton
                    onClick={() => onRemove(file.id)}
                    sx={{
                      backgroundColor: 'error.main',
                      color: 'white',
                      '&:hover': {
                        backgroundColor: 'error.dark',
                      },
                    }}
                  >
                    <Close />
                  </IconButton>
                </Box>
              </Paper>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Dropzone */}
      <Paper
        {...getRootProps()}
        sx={{
          p: 3,
          border: '2px dashed',
          borderRadius: 2,
          textAlign: 'center',
          transition: 'all 0.3s',
          ...getDropzoneStyle(),
        }}
      >
        <input {...getInputProps()} />
        
        <CloudUpload sx={{ fontSize: 48, color: theme.palette.grey[400], mb: 2 }} />
        
        {files.length >= maxFiles ? (
          <Typography variant="body1" color="text.secondary">
            {language === 'ar'
              ? `تم الوصول إلى الحد الأقصى (${maxFiles} ملفات)`
              : `Maximum files reached (${maxFiles} files)`
            }
          </Typography>
        ) : isDragActive ? (
          <Typography variant="body1" color="primary">
            {isDragAccept
              ? (language === 'ar' ? 'أفلت الملفات هنا...' : 'Drop files here...')
              : (language === 'ar' ? 'نوع الملف غير مدعوم' : 'File type not supported')
            }
          </Typography>
        ) : (
          <>
            <Typography variant="body1" gutterBottom>
              {language === 'ar' 
                ? 'اسحب وأفلت الملفات هنا أو انقر للاختيار'
                : 'Drag and drop files here or click to select'
              }
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {language === 'ar'
                ? `الصور والفيديوهات المدعومة • حتى ${maxFiles} ملفات • ${(maxSize / 1024 / 1024).toFixed(0)}MB لكل ملف`
                : `Supported images and videos • Up to ${maxFiles} files • ${(maxSize / 1024 / 1024).toFixed(0)}MB per file`
              }
            </Typography>
          </>
        )}
      </Paper>
      
      {files.length > 0 && (
        <Box display="flex" justifyContent="space-between" mt={1}>
          <Typography variant="caption" color="text.secondary">
            {language === 'ar'
              ? `${files.length} من ${maxFiles} ملفات`
              : `${files.length} of ${maxFiles} files`
            }
          </Typography>
          <Box display="flex" gap={1}>
            {files.filter(f => f.type === 'image').length > 0 && (
              <Box display="flex" alignItems="center" gap={0.5}>
                <ImageIcon fontSize="small" color="action" />
                <Typography variant="caption" color="text.secondary">
                  {files.filter(f => f.type === 'image').length}
                </Typography>
              </Box>
            )}
            {files.filter(f => f.type === 'video').length > 0 && (
              <Box display="flex" alignItems="center" gap={0.5}>
                <VideoLibrary fontSize="small" color="action" />
                <Typography variant="caption" color="text.secondary">
                  {files.filter(f => f.type === 'video').length}
                </Typography>
              </Box>
            )}
          </Box>
        </Box>
      )}
    </Box>
  );
};