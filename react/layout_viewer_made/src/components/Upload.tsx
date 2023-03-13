import { Button, Upload, UploadProps } from 'antd'
import { UploadOutlined } from '@ant-design/icons'

const props: UploadProps = {
   name: 'file',
   action: '/difference/',
   headers: {
      authorization: 'authorization-text',
   },
   onChange(info) {
      if (info.file.status !== 'uploading') {
         console.debug(info.file, info.fileList)
      }
      if (info.file.status === 'done') {
         message.success(`${info.file.name} file uploaded successfully`)
      } else if (info.file.status === 'error') {
         message.error(`${info.file.name} file upload failed.`)
      }
   },
}

const UploadDocument: React.FC = () => (
   <Upload {...props}>
      <Button style={{ width: '135%' }} icon={<UploadOutlined />}>
         Click to Upload
      </Button>
   </Upload>
)

export default UploadDocument
