import { Link } from 'react-router-dom'
import useTitle from '../useTitle'
export default function NotFound() {
  useTitle('Not found')
  return (<section><h1>Page not found</h1><Link to="/">Home</Link></section>)
}
