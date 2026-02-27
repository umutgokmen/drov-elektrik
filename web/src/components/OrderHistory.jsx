import React from 'react';
import { X, Clock, ChevronRight } from 'lucide-react';

/**
 * OrderHistory modal - displays past saved orders and allows reloading them.
 *
 * Props:
 *   orders      - array of order objects from the API
 *   boxModels   - array of available box model objects (for name lookup)
 *   onLoad      - (order) => void  called when the user clicks an order to reload it
 *   onClose     - () => void       called when the user closes the modal
 */
export default function OrderHistory({ orders, boxModels, onLoad, onClose }) {
  const getBoxName = (boxId) => {
    const box = boxModels.find((b) => b.id === boxId);
    return box ? box.name : boxId.toUpperCase();
  };

  const formatDate = (isoString) => {
    return new Date(isoString).toLocaleString(navigator.language, {
      dateStyle: 'short',
      timeStyle: 'short',
    });
  };

  return (
    <div className="order-history-overlay" onClick={onClose}>
      <div
        className="order-history-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="order-history-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Clock size={16} />
            <span>Order History</span>
          </div>
          <button className="order-history-close" onClick={onClose}>
            <X size={16} />
          </button>
        </div>

        <div className="order-history-body">
          {orders.length === 0 ? (
            <div className="order-history-empty">No saved orders yet.</div>
          ) : (
            <ul className="order-history-list">
              {orders.map((order) => (
                <li key={order.id} className="order-history-item">
                  <div className="order-history-item-info">
                    <div className="order-history-item-title">
                      {order.name || `Order #${order.id}`}
                    </div>
                    <div className="order-history-item-meta">
                      <span>{getBoxName(order.box_id)}</span>
                      <span>&middot;</span>
                      <span>{order.terminals} terminals</span>
                      <span>&middot;</span>
                      <span>
                        {order.holes_top + order.holes_bottom + order.holes_left + order.holes_right} holes
                      </span>
                      <span>&middot;</span>
                      <span>{formatDate(order.created_at)}</span>
                    </div>
                  </div>
                  <button
                    className="order-history-load-btn"
                    onClick={() => onLoad(order)}
                    title="Load this configuration"
                  >
                    <ChevronRight size={16} />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
