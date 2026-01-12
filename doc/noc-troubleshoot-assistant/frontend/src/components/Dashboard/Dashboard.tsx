import { Box, Divider } from '@mui/material';
import InstanceCards from './InstanceCards';
import AlarmTable from '../Alarms/AlarmTable';

export default function Dashboard() {
  return (
    <Box>
      <InstanceCards />
      <Divider sx={{ my: 3 }} />
      <AlarmTable />
    </Box>
  );
}
